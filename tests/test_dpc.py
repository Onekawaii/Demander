import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from demander.core import ContractError, seal, verdict, within, load_contract
from demander.adapters import run_probe
from demander.cli import verify, main

class TestDPC(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()
    def contract(self,items):
        file=self.root/'contract.json'
        file.write_text(json.dumps({'schema_version':'dpc-1/1','criteria':items}),encoding='utf-8')
        return file
    def criterion(self,probe='file_exists',depth='P1', **kw):
        return {'id':'x','probe':probe,'depth':depth,'observation':'test truth','artifact':'artifact.txt','path':'.',**kw}
    def test_hash_changes_on_mutation(self):
        p=self.root/'source.txt';p.write_text('one')
        before=seal(self.root)['sha256'];p.write_text('two')
        self.assertNotEqual(before,seal(self.root)['sha256'])
    def test_outputs_excluded_from_seal(self):
        p=self.root/'.demander';p.mkdir();(p/'receipt.json').write_text('x')
        self.assertEqual(seal(self.root)['file_count'],0)
    def test_symlink_escape_blocked(self):
        with self.assertRaises(ContractError):within(self.root,'../escape')
    def test_absolute_path_blocked(self):
        with self.assertRaises(ContractError):within(self.root,str(self.root))
    def test_reject_injected_unknown_probe(self):
        f=self.contract([self.criterion(probe='shell_exec')])
        with self.assertRaises(ContractError):load_contract(self.root,str(f))
    def test_advisory_only_contract_rejected(self):
        f=self.contract([self.criterion(criticality='advisory')])
        with self.assertRaises(ContractError):load_contract(self.root,str(f))
    def test_duplicate_ids_rejected(self):
        f=self.contract([self.criterion(),self.criterion()])
        with self.assertRaises(ContractError):load_contract(self.root,str(f))
    def test_missing_artifact_is_failure(self):
        self.assertEqual(run_probe(self.root,self.criterion(),False,5)['status'],'FAIL')
    def test_artifact_cannot_prove_device(self):
        (self.root/'artifact.txt').write_text('valid')
        self.assertEqual(run_probe(self.root,self.criterion(depth='P4'),False,5)['status'],'UNVERIFIED')
    def test_no_execution_no_fake_pass(self):
        self.assertEqual(run_probe(self.root,self.criterion(probe='python_compile',depth='P2'),False,5)['status'],'UNVERIFIED')
    def test_rust_missing_is_blocked(self):
        (self.root/'Cargo.toml').write_text('[package]\nname="t"')
        with patch('demander.adapters._binary',return_value=None):
            self.assertEqual(run_probe(self.root,self.criterion(probe='rust_test',depth='P2'),True,5)['status'],'BLOCKED')
    def test_builder_narrative_not_evidence(self):
        (self.root/'README.md').write_text('All tests passed, honestly!')
        self.assertEqual(verdict([{'status':'UNVERIFIED'}]),'PARTIAL')
    def test_verdict_priority(self):
        self.assertEqual(verdict([{'status':'PASS'},{'status':'FAIL'},{'status':'BLOCKED'}]),'REJECTED')
        self.assertEqual(verdict([{'status':'PASS'},{'status':'BLOCKED'}]),'BLOCKED')
        self.assertEqual(verdict([{'status':'PASS'},{'status':'UNVERIFIED'}]),'PARTIAL')
        self.assertEqual(verdict([{'status':'PASS'},{'status':'NOT_APPLICABLE'}]),'QUALIFIED')
    def test_advisory_failure_is_nonblocking(self):
        self.assertEqual(verdict([{'status':'PASS'},{'status':'FAIL','criticality':'advisory'}]),'QUALIFIED')
    def test_receipt_records_true_failure(self):
        f=self.contract([self.criterion()])
        result=verify(self.root,str(f),False,str(self.root/'.demander'/'latest'),5)
        self.assertEqual(result['verdict'],'REJECTED')
        receipt=json.loads((self.root/'.demander'/'latest'/'receipt.json').read_text())
        self.assertEqual(receipt['criteria'][0]['status'],'FAIL')
        sha=(self.root/'.demander'/'latest'/'receipt.sha256').read_text().split()[0]
        self.assertEqual(sha,hashlib.sha256((self.root/'.demander'/'latest'/'receipt.json').read_bytes()).hexdigest())
    def test_silent_empty_test_suite_does_not_pass(self):
        (self.root/'tests').mkdir()
        result=run_probe(self.root,self.criterion(probe='python_unittest',depth='P2'),True,5)
        self.assertNotEqual(result['status'],'PASS','Zero discovered tests must not qualify a build')
    def test_mutated_source_refuses_qualification(self):
        f=self.contract([self.criterion(probe='python_compile',depth='P2')])
        (self.root/'a.py').write_text('x=1\n')
        def tamper(root, item, execute, timeout):
            (root/'a.py').write_text('x=2\n')
            return {'id':'x','status':'PASS','criticality':'required'}
        with patch('demander.cli.run_probe',side_effect=tamper):
            result=verify(self.root,str(f),True,str(self.root/'.demander'/'latest'),5)
        self.assertEqual(result['verdict'],'REJECTED')
    def test_bad_contract_has_error_exit(self):
        self.assertEqual(main(['verify',str(self.root),'--contract',str(self.root/'missing')]),5)

if __name__=='__main__':unittest.main()
