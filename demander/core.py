"""DPC-1 source sealing, scope validation, verdicts, evidence and receipts."""
from __future__ import annotations
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any

EXCLUDED_DIRS = {'.git', '.demander', '__pycache__', 'node_modules', '.venv', 'venv', 'target', 'dist', 'build', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.next'}
EXCLUDED_SUFFIXES = {'.pyc', '.pyo'}
STATUS_ORDER = ('FAIL', 'BLOCKED', 'UNVERIFIED', 'PASS', 'NOT_APPLICABLE')
DEPTHS = ('P0','P1','P2','P3','P4')

class ContractError(ValueError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def within(root: pathlib.Path, value: str) -> pathlib.Path:
    if not isinstance(value, str) or not value or pathlib.Path(value).is_absolute():
        raise ContractError(f'Path must be relative to project root: {value!r}')
    dest = (root / value).resolve()
    if not dest.is_relative_to(root.resolve()):
        raise ContractError(f'Path escapes project root: {value!r}')
    return dest


def seal(root: pathlib.Path) -> dict[str, Any]:
    root = root.resolve()
    files = []
    for directory, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS and not (pathlib.Path(directory)/d).is_symlink())
        for name in sorted(names):
            p = pathlib.Path(directory) / name
            if p.is_symlink() or p.suffix in EXCLUDED_SUFFIXES:
                continue
            rel = p.relative_to(root).as_posix()
            try:
                data = p.read_bytes()
            except (OSError, PermissionError) as exc:
                raise ContractError(f'Could not seal {rel}: {exc}') from exc
            files.append({'path': rel, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
    canonical = json.dumps(files, sort_keys=True, separators=(',', ':')).encode()
    return {'sha256': hashlib.sha256(canonical).hexdigest(), 'file_count':len(files), 'files': files,
            'excluded_directories': sorted(EXCLUDED_DIRS)}


def git_identity(root: pathlib.Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, cmd in (('head', ['git','rev-parse','HEAD']), ('branch',['git','branch','--show-current']), ('status',['git','status','--porcelain'])):
        try:
            p = subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=3,check=False)
            if p.returncode == 0:
                result[key] = p.stdout.strip()[:5000]
        except (OSError, subprocess.TimeoutExpired):
            pass
    return result


def load_contract(root: pathlib.Path, filename: str) -> dict:
    path = pathlib.Path(filename).resolve()
    if not path.is_file():
        raise ContractError(f'Contract not found: {filename}')
    try:
        config = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f'Invalid JSON contract: {exc}') from exc
    if not isinstance(config, dict) or config.get('schema_version') != 'dpc-1/1':
        raise ContractError('Contract schema_version must be dpc-1/1')
    criteria = config.get('criteria')
    if not isinstance(criteria,list) or not criteria:
        raise ContractError('Contract requires nonempty criteria list')
    if not any(isinstance(c,dict) and c.get('criticality','required') == 'required' for c in criteria):
        raise ContractError('At least one required criterion must be declared')
    seen = set()
    supported = {'file_exists','python_compile','python_unittest','typescript_typecheck','typescript_test','rust_check','rust_test'}
    for c in criteria:
        if not isinstance(c, dict) or not isinstance(c.get('id'),str) or not c['id'].strip() or c['id'] in seen:
            raise ContractError('Criterion IDs must be unique nonempty strings')
        seen.add(c['id'])
        if c.get('probe') not in supported:
            raise ContractError(f"Unsupported probe: {c.get('probe')!r}")
        if c.get('depth') not in DEPTHS:
            raise ContractError(f"Invalid depth in {c['id']}")
        if c.get('criticality', 'required') not in ('required','advisory'):
            raise ContractError(f"Invalid criticality in {c['id']}")
        if not isinstance(c.get('observation'),str) or not c['observation'].strip():
            raise ContractError(f"Observation missing in {c['id']}")
        dest = within(root, c.get('path','.'))
        if c['probe'] == 'file_exists' and not isinstance(c.get('artifact'),str):
            raise ContractError(f"Artifact path missing in {c['id']}")
        if c['probe'] == 'file_exists':
            within(root, c['artifact'])
    return config


def verdict(criteria: list[dict[str,Any]]) -> str:
    required = [c['status'] for c in criteria if c.get('criticality','required') == 'required']
    if 'FAIL' in required:
        return 'REJECTED'
    if 'BLOCKED' in required:
        return 'BLOCKED'
    if 'UNVERIFIED' in required:
        return 'PARTIAL'
    return 'QUALIFIED'


def receipt_write(out_dir: pathlib.Path, receipt: dict[str,Any]) -> tuple[pathlib.Path,pathlib.Path]:
    out_dir.mkdir(parents=True,exist_ok=True)
    path = out_dir / 'receipt.json'
    data = json.dumps(receipt,indent=2,sort_keys=True,ensure_ascii=False) + '\n'
    path.write_text(data, encoding='utf-8')
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    (out_dir/'receipt.sha256').write_text(f'{digest}  receipt.json\n',encoding='ascii')
    lines = ['# Demander Proof Circuit — verification receipt', '',f"Verdict: **{receipt['verdict']}**",f"Project seal: `{receipt['source_after']['sha256']}`", f"Run: `{receipt['run_id']}`",'', '| Criterion | Status | Actual observation |', '|---|---|---|']
    for item in receipt['criteria']:
        detail = str(item.get('detail','')).replace('|','/').replace('\n',' ')
        lines.append(f"| {item['id']} | {item['status']} | {detail[:180]} |")
    lines += ['', 'Execution limitations:', '- Project-provided tests can execute arbitrary code when --execute is supplied.', '- Network isolation and OS-level sandboxing are NOT implemented in this alpha.', '- A PASS applies only to its declared criterion and proof depth.']
    md = out_dir/'report.md'
    md.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return path, md
