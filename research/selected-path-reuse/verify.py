#!/usr/bin/env python3
"""Opt-in metadata-check proposal, no supplier/native scientific replay.

Prepared for zhaobenny with gpt-6.1-sol at high reasoning effort. Apache-2.0.
Path-reuse mechanism: Arham Tahir, PR2793.
Douglas Colkitt's checker and credited predecessor tests supply the controls.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import importlib
import io
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time
from types import ModuleType
import unittest

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
TESTS = ('test_selected_proof_binding', 'test_selected_explicit_inventory',
         'test_selected_inventory_links')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def variants():
    pins = json.loads((PACKAGE / 'SOURCES.json').read_bytes())
    for row in pins['files']:
        if row['usage'] == 'input':
            require(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                    'Live source changed: ' + row['path'])
    with tempfile.TemporaryDirectory() as td:
        tree = Path(td)
        (tree / 'scripts').mkdir()
        target = tree / 'scripts/verify_selected_result.py'
        original = (ROOT / 'scripts/verify_selected_result.py').read_bytes()
        target.write_bytes(original)
        patch = PACKAGE / 'proposal.patch'
        # Apply only in this temporary tree. The selected checker stays pinned.
        subprocess.run(['git', 'apply', '--check', str(patch)], cwd=tree, check=True,
                       capture_output=True, timeout=10)
        subprocess.run(['git', 'apply', str(patch)], cwd=tree, check=True,
                       capture_output=True, timeout=10)
        changed = target.read_bytes()
    result = []
    for name, raw in (('original', original), ('proposal', changed)):
        module = ModuleType('selected_' + name)
        # Preserve the real ROOT used by default-argument bindings, but execute
        # authenticated source bytes rather than importing cached bytecode.
        module.__file__ = str(ROOT / 'scripts/verify_selected_result.py')
        exec(compile(raw, module.__file__, 'exec'), module.__dict__)
        result.append(module)
    return result


def suites(checker):
    sys.path.insert(0, str(ROOT / 'tests'))
    count = 0
    for name in TESTS:
        module = importlib.import_module(name)
        module.checker = checker
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        # This CLI control executes the unmodified source on disk. Do not count
        # it as exercising the proposed implementation.
        filtered = unittest.TestSuite()
        for group in suite:
            for test in group:
                if test._testMethodName != 'test_optimized_cli_still_fails_closed':
                    filtered.addTest(test)
        report = unittest.TextTestRunner(stream=io.StringIO()).run(filtered)
        require(report.wasSuccessful() and not report.skipped,
                name + ' failed: ' + repr(report.errors + report.failures + report.skipped))
        count += report.testsRun
    return count


def invalidation(checker):
    fixture = importlib.import_module('test_selected_proof_binding').fixture
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        record = fixture(root)
        manifest = root / record['source_manifest']
        data = json.loads(manifest.read_bytes())
        data['format'] = 'repository-files-sha256-v1'
        del data['package_roots']
        manifest.write_text(json.dumps(data))
        source = root / 'supplier/PROOF.md'
        original = source.read_bytes()
        require(checker.check(record, root) > 0, 'positive control')
        def rejects():
            try:
                checker.check(record, root)
            except (ValueError, OSError):
                return
            raise ValueError('Mutation accepted')
        source.write_bytes(original + b'changed')
        rejects()
        source.write_bytes(original)
        checker.check(record, root)
        source.unlink()
        rejects()
        source.write_bytes(original)
        checker.check(record, root)
        # Same name and bytes, now a forbidden alias after a successful call.
        source.rename(root / 'held.md')
        source.symlink_to(root / 'held.md')
        rejects()
        source.unlink()
        (root / 'held.md').rename(source)
        checker.check(record, root)
        # A newly listed input must be hashed on the next call, too.
        data['files']['decoy.md'] = '0' * 64
        manifest.write_text(json.dumps(data))
        rejects()
    return 4


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--benchmark', type=Path)
    args = parser.parse_args()
    original, proposal = variants()
    # PR2793 predates the explicit-file schema. Exercise only a tiny fixture,
    # not its historical complete replay or a walk of today's certificates.
    predecessor = ModuleType('predecessor')
    predecessor.__file__ = str(ROOT / 'research/selected-preflight-path-reuse/candidate.py')
    exec(compile((ROOT / 'research/selected-preflight-path-reuse/candidate.py').read_bytes(),
                 predecessor.__file__, 'exec'), predecessor.__dict__)
    sys.path.insert(0, str(ROOT / 'tests'))
    fixture = importlib.import_module('test_selected_proof_binding').fixture
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        record = fixture(root)
        manifest = root / record['source_manifest']
        data = json.loads(manifest.read_bytes())
        data['format'] = 'repository-files-sha256-v1'
        del data['package_roots']
        manifest.write_text(json.dumps(data))
        require(original.check(record, root) == proposal.check(record, root),
                'Explicit fixture differs')
        try:
            predecessor.check(record, root)
        except ValueError as error:
            require(str(error) == 'Selected package inventory or bytes changed',
                    'Unexpected predecessor rejection')
        else:
            raise ValueError('Expected predecessor explicit-format incompatibility')
    tests = [suites(module) for module in (original, proposal)]
    controls = [invalidation(module) for module in (original, proposal)]
    record = json.loads((ROOT / 'certificates/selected-result.json').read_bytes())
    require(original.check(record) == proposal.check(record), 'Selected result differs')
    if args.benchmark:
        samples = {'original': [], 'proposal': []}
        for trial in range(9):
            for module in ((original, proposal) if trial % 2 == 0 else (proposal, original)):
                name = module.__name__.removeprefix('selected_')
                started = time.perf_counter()
                module.check(record)
                samples[name].append(time.perf_counter() - started)
        medians = {k: statistics.median(v) for k, v in samples.items()}
        result = dict(samples_seconds=samples, medians_seconds=medians,
                      ratio=medians['proposal']/medians['original'],
                      python=sys.version, platform=platform.platform(),
                      selected_record_sha256=sha256((ROOT/'certificates/selected-result.json').read_bytes()).hexdigest(),
                      fixture='Full selected check, in-process, warm filesystem, nine alternating pairs')
        args.benchmark.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status='PASS_SELECTED_PATH_REUSE_PROPOSAL', tests_per_variant=tests,
                         invalidation_controls_per_variant=controls,
                         selected_result_equal=True, predecessor_explicit_schema_rejects=True, scope='Metadata only; stable filesystem; no cross-call cache'),
                     sort_keys=True))


if __name__ == '__main__':
    main()
