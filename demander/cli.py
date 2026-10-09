"""Offline-first Demander CLI; no user config executes without explicit authorization."""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import shutil
import sys
import uuid
from . import __version__
from .adapters import run_probe
from .core import ContractError, git_identity, load_contract, now, receipt_write, seal, verdict


def inspect(root: pathlib.Path) -> dict:
    targets = []
    import os
    from .core import EXCLUDED_DIRS
    markers = {'package.json':'typescript','tsconfig.json':'typescript','Cargo.toml':'rust',
               'pyproject.toml':'python','project.godot':'godot'}
    for directory,dirs,files in os.walk(root,followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS and not (pathlib.Path(directory)/d).is_symlink())
        for marker,adapter in markers.items():
            if marker in files:
                p=pathlib.Path(directory)/marker
                targets.append({'path':p.parent.relative_to(root).as_posix(), 'adapter':adapter,'marker':marker})
    return {'version':__version__,'root':str(root),'targets':targets,'source':seal(root), 'git':git_identity(root),'toolchains':{cmd:bool(shutil.which(cmd)) for cmd in ('python','node','tsc','cargo','godot')}, 'execution_performed':False}


def verify(root: pathlib.Path,contract_path:str,execute:bool,output:str,timeout:int)->dict:
    contract=load_contract(root,contract_path)
    before=seal(root)
    start=now()
    criteria=[]
    for item in contract['criteria']:
        criteria.append(run_probe(root,item,execute,timeout))
    after=seal(root)
    if before['sha256']!=after['sha256']:
        criteria.append({'id':'DPC-SOURCE-IMMUTABILITY','probe':'source_seal','depth':'P1','criticality':'required','status':'FAIL','detail':'Relevant source changed during verification; compare seals and run fresh verification.'})
    run_id=uuid.uuid4().hex[:16]
    receipt={'schema_version':'dpc-receipt/1','engine_version':__version__,'method':'DPC-1', 'run_id':run_id, 'started_at':start, 'ended_at':now(), 'root':str(root), 'git':git_identity(root),'contract_id':contract.get('contract_id','unnamed'),'authorized_execution':execute,'network_isolation':'NOT ENFORCED', 'source_before':before,'source_after':after,'criteria':criteria,'verdict':verdict(criteria),'limits':{'timeout_seconds_per_command':timeout,'sandbox':'none; authorized tests run as current user'}}
    dest=pathlib.Path(output).resolve()
    receipt_write(dest,receipt)
    return {'run_id':run_id,'verdict':receipt['verdict'],'criteria':[{k:item.get(k,'') for k in ('id','status','detail')} for item in criteria],'receipt':str(dest/'receipt.json'),'report':str(dest/'report.md')}


def main(argv:list[str]|None=None)->int:
    parser=argparse.ArgumentParser(prog='demander',description='DEMANDER UNIVERSAL — DPC-1 independent verification alpha')
    parser.add_argument('--version',action='version',version=__version__)
    sub=parser.add_subparsers(dest='action',required=True)
    i=sub.add_parser('inspect',help='Read-only project inventory (does not run project tests)')
    i.add_argument('project',nargs='?',default='.')
    v=sub.add_parser('verify',help='Execute a DPC-1 contract and produce evidence receipts')
    v.add_argument('project',nargs='?',default='.')
    v.add_argument('--contract',required=True)
    v.add_argument('--execute',action='store_true',help='Explicitly authorize local project-defined test code to run')
    v.add_argument('--out',default=None)
    v.add_argument('--timeout',type=int,default=60)
    r=sub.add_parser('report',help='Read an existing JSON receipt and show its verdict')
    r.add_argument('receipt')
    args=parser.parse_args(argv)
    try:
        if args.action=='report':
            p=pathlib.Path(args.receipt)
            data=json.loads(p.read_text(encoding='utf-8'))
            if data.get('schema_version')!='dpc-receipt/1':
                raise ContractError('Unsupported receipt format')
            print(json.dumps({'verdict':data['verdict'],'run_id':data['run_id'],'contract_id':data['contract_id']},indent=2))
            return 0
        root=pathlib.Path(args.project).resolve()
        if not root.is_dir():
            raise ContractError(f'Project does not exist: {root}')
        if args.action=='inspect':
            print(json.dumps(inspect(root),indent=2))
            return 0
        if not 1<=args.timeout<=120:
            raise ContractError('Timeout must be between 1 and 120 seconds')
        output=args.out or str(root/'.demander'/'latest')
        result=verify(root,args.contract,args.execute,output,args.timeout)
        print(json.dumps(result,indent=2))
        return {'QUALIFIED':0,'PARTIAL':2,'BLOCKED':3,'REJECTED':4}[result['verdict']]
    except (ContractError, ValueError, KeyError, OSError) as exc:
        print(f'DEMANDER ERROR: {exc}',file=sys.stderr)
        return 5

if __name__=='__main__':
    sys.exit(main())
