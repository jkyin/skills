#!/usr/bin/env python3
"""Offline installation recovery, Git base, and unchanged business-rule checks."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('linker', ROOT / 'scripts/link_installed.py')
linker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(linker)
checks = []
with tempfile.TemporaryDirectory(prefix='guruclub-rollback-') as directory:
    home = Path(directory)
    for parent, names in linker.ENTRIES.items():
        for name in names:
            path = home / parent / name
            path.mkdir(parents=True)
            (path / 'SKILL.md').write_text(name)
    before = linker.plan(home)
    original, counter = Path.symlink_to, [0]
    def fail_second(self, *args, **kwargs):
        counter[0] += 1
        if counter[0] == 2:
            raise OSError('simulated link failure')
        return original(self, *args, **kwargs)
    Path.symlink_to = fail_second
    try:
        try:
            linker.apply(home, before)
        except OSError:
            pass
        else:
            raise AssertionError('Failure was not injected')
    finally:
        Path.symlink_to = original
    assert linker.plan(home) == before
    checks.append('Mid-install failure restores original entries')
with tempfile.TemporaryDirectory(prefix='guruclub-base-') as directory:
    repo = Path(directory)
    def git(*args):
        return subprocess.check_output(
            ['git', '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null', *args],
            cwd=repo, text=True, stderr=subprocess.PIPE).strip()
    git('init', '-b', 'develop')
    git('config', 'user.name', 'Offline Fixture')
    git('config', 'user.email', 'fixture@example.invalid')
    (repo / 'feature.txt').write_text('before\n')
    git('add', 'feature.txt')
    git('commit', '-m', 'fixture base')
    git('branch', 'main')
    git('checkout', '-b', 'feature')
    (repo / 'feature.txt').write_text('after\n')
    git('commit', '-am', 'fixture change')
    for branch in ['feature', 'develop', 'main']:
        git('update-ref', 'refs/remotes/origin/' + branch, branch)
    git('config', 'remote.origin.url', str(repo))
    git('config', 'remote.origin.fetch', '+refs/heads/*:refs/remotes/origin/*')
    git('branch', '--set-upstream-to', 'origin/feature')
    git('symbolic-ref', 'refs/remotes/origin/HEAD', 'refs/remotes/origin/main')
    assert git('diff', 'origin/feature...HEAD') == ''
    expected = git('diff', 'origin/develop...HEAD')
    assert 'after' in expected
    base = git('merge-base', 'origin/develop', 'HEAD')
    assert git('diff', base, 'HEAD') == expected
    checks.append('Feature upstream hides changes; develop base retains them; merge-base endpoint diff is equivalent')
manifest = json.loads((ROOT / 'sources.json').read_text())
for row in manifest['files']:
    path = row['path']
    if path.endswith(('commit_activity.py', 'agents/openai.yaml')) or path.startswith('source-variants/'):
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == row['sha256'], path
checks.append('Business computation, explicit invocation metadata and source variants unchanged')
for path in ROOT.rglob('*.md'):
    if 'source-variants' in path.parts:
        continue
    for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if '://' not in target and not target.startswith('#'):
            assert (path.parent / target.split('#')[0]).exists(), (str(path), target)
checks.append('Current Markdown local reference targets exist')
result = {'passed': checks, 'scope': 'offline fixtures and static integrity checks'}
(ROOT / 'validation/behavior-checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
