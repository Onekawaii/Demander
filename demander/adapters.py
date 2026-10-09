"""Fixed, inspectable project probes (no shell, no npx/download-on-demand)."""
from __future__ import annotations
import hashlib
import pathlib
import re
import shutil
import subprocess
import sys
import time
from typing import Any
from .core import within, DEPTHS


def _binary(name: str) -> str | None:
    return shutil.which(name)


def _command_for(root: pathlib.Path, item: dict) -> tuple[list[str] | None, str]:
    probe = item['probe']
    work = within(root,item.get('path','.'))
    if not work.is_dir():
        return None, f'Target directory missing: {work}'
    if probe == 'python_compile':
        paths = sorted(str(p) for p in work.rglob('*.py') if not any(x in p.parts for x in ('.venv','venv','__pycache__')))
        if not paths:
            return None, 'No Python sources found'
        return [sys.executable, '-m', 'py_compile', *paths], ''
    if probe == 'python_unittest':
        return [sys.executable, '-m','unittest','discover','-s','tests','-p','test*.py','-v'], ''
    if probe == 'typescript_typecheck':
        local_bin = work/'node_modules'/'.bin'/('tsc.cmd' if sys.platform == 'win32' else 'tsc')
        tsc = str(local_bin) if local_bin.is_file() else _binary('tsc')
        if not tsc:
            return None, 'TypeScript compiler unavailable (no local or global tsc); no npx downloads attempted'
        if not (work/'tsconfig.json').exists():
            return None, 'tsconfig.json missing'
        return [tsc,'--noEmit','--project','tsconfig.json'], ''
    if probe == 'typescript_test':
        if not (work/'package.json').is_file():
            return None, 'package.json missing'
        npm = _binary('npm.cmd' if sys.platform == 'win32' else 'npm')
        return ([npm, 'test', '--', '--run'] if npm else None), ('npm unavailable' if not npm else '')
    if probe in ('rust_check','rust_test'):
        cargo = _binary('cargo')
        if not cargo:
            return None, 'Rust cargo toolchain unavailable'
        if not (work/'Cargo.toml').is_file():
            return None, 'Cargo.toml missing'
        return [cargo, 'check' if probe == 'rust_check' else 'test', '--offline'], ''
    return None, 'Unknown probe'


def run_probe(root:pathlib.Path,item:dict,execute:bool,timeout:int)->dict[str,Any]:
    start=time.monotonic()
    probe=item['probe']
    depth=item['depth']
    result={'id':item['id'],'probe':probe,'depth':depth,'criticality':item.get('criticality','required'), 'status':'UNVERIFIED','detail':'','command':None,'exit_code':None,'elapsed_seconds':0.0}
    if probe=='file_exists':
        file = within(root,item['artifact'])
        if file.is_file():
            result.update(status='PASS' if DEPTHS.index(depth)<=1 else 'UNVERIFIED',detail='Artifact exists and SHA-256 recorded; no runtime behavior verified',sha256=hashlib.sha256(file.read_bytes()).hexdigest())
        else:
            result.update(status='FAIL',detail=f'Artifact absent: {item["artifact"]}')
        return result
    if not execute:
        result['detail']='Execution NOT authorized: rerun with --execute'
        return result
    if DEPTHS.index(depth)>2:
        result['detail']=f'{depth} requires additional runtime/device evidence; CLI probe proves at most P2'
        return result
    cmd,error=_command_for(root,item)
    if cmd is None:
        result.update(status='BLOCKED',detail=error)
        return result
    result['command']=cmd
    work=within(root,item.get('path','.'))
    try:
        output=subprocess.run(cmd,cwd=work,capture_output=True,text=True,errors='replace',timeout=timeout,check=False,stdin=subprocess.DEVNULL)
        result['exit_code']=output.returncode
        result['stdout']=output.stdout[-12000:]
        result['stderr']=output.stderr[-12000:]
        result['status']='PASS' if output.returncode==0 else 'FAIL'
        result['detail']=f'Process exited with code {output.returncode}; no human/device runtime verification claimed'
        if probe == 'python_unittest' and output.returncode == 0:
            counts = re.findall(r'Ran (\d+) tests? in ', output.stdout+'\n'+output.stderr)
            if not counts or int(counts[-1]) == 0:
                result.update(status='FAIL',detail='No test count or zero tests discovered; a zero-test suite cannot establish success')
    except subprocess.TimeoutExpired as exc:
        result.update(status='FAIL',detail=f'Authorized check exceeded {timeout}s timeout',stdout=str(exc.stdout or '')[-2000:],stderr=str(exc.stderr or '')[-2000:])
    except OSError as exc:
        result.update(status='BLOCKED',detail=f'Unable to start tool: {exc}')
    result['elapsed_seconds']=round(time.monotonic()-start,3)
    return result
