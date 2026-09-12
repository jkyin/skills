#!/usr/bin/env python3
"""Preview or link existing personal skill entries to this repository, with backups."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = {
    '.codex/skills': ['guruclub-weekly-report', 'guruclub-monthly-summary', 'guru-mr-description'],
    '.agents/skills': ['guru-commit', 'guru-code-review', 'guru-mr-description'],
    '.claude/skills': ['guru-commit', 'guru-code-review', 'guru-mr-description',
                       'guruclub-weekly-report', 'guruclub-monthly-summary'],
}


def fingerprint(path):
    if path.is_symlink():
        return {'type': 'symlink', 'target': os.readlink(path)}
    if not path.exists():
        return {'type': 'missing'}
    if not path.is_dir():
        raise ValueError(f'Expected a skill directory or symlink: {path}')
    records = []
    for child in sorted(path.rglob('*')):
        rel = str(child.relative_to(path))
        if child.is_symlink():
            records.append([rel, 'symlink', os.readlink(child)])
        elif child.is_file():
            records.append([rel, 'file', hashlib.sha256(child.read_bytes()).hexdigest()])
        elif child.is_dir():
            records.append([rel, 'directory'])
        else:
            raise ValueError(f'Unsupported entry: {child}')
    digest = hashlib.sha256(json.dumps(records, ensure_ascii=False).encode()).hexdigest()
    return {'type': 'directory', 'sha256': digest, 'entries': len(records)}


def plan(home):
    entries = []
    for parent, names in ENTRIES.items():
        for name in names:
            source = ROOT / name
            if not (source / 'SKILL.md').is_file():
                raise ValueError(f'Missing repository skill: {source}')
            path = home / parent / name
            before = fingerprint(path)
            if before['type'] == 'missing':
                action = 'skip-missing'
            elif path.is_symlink() and path.resolve() == source:
                action = 'already-linked'
            else:
                action = 'backup-and-link'
            entries.append({'path': str(path), 'relative': str(path.relative_to(home)),
                            'target': str(source), 'before': before, 'action': action})
    return {'home': str(home), 'repository': str(ROOT), 'entries': entries}


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


RENAMED_SKILLS = {'commit-expert': 'guru-commit'}


def restore(manifest_path):
    record = json.loads(manifest_path.read_text())
    entries = record['entries']
    operations = []
    for entry in entries:
        destination, backup = Path(entry['path']), Path(entry['backup'])
        path, expected = destination, entry['target']
        # Older backup manifests retain the pre-rename destination and target.
        renamed = RENAMED_SKILLS.get(destination.name)
        if renamed and not os.path.lexists(destination):
            path = destination.with_name(renamed)
            expected = str(Path(expected).with_name(renamed))
        if not path.is_symlink() or os.readlink(path) != expected:
            raise ValueError(f'Entry changed since installation; refusing restore: {path}')
        if not os.path.lexists(backup):
            raise ValueError(f'Missing backup: {backup}')
        operations.append((path, destination, backup))
    for path, destination, backup in reversed(operations):
        path.unlink()
        os.replace(backup, destination)
    record['restored_at'] = dt.datetime.now().astimezone().isoformat()
    save(manifest_path, record)
    return {'restored': len(entries), 'manifest': str(manifest_path)}


def apply(home, expected):
    current = plan(home)
    if current != expected:
        raise ValueError('Installation entries changed since preview; regenerate and inspect the plan')
    changes = [e for e in current['entries'] if e['action'] == 'backup-and-link']
    if not changes:
        return {'linked': 0, 'message': 'All existing entries already link to this repository'}
    stamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup_root = home / '.codex/backups' / ('guruclub-skills-' + stamp)
    backup_root.mkdir(parents=True, exist_ok=False)
    manifest = backup_root / 'restore.json'
    record = {'repository': str(ROOT), 'entries': []}
    save(manifest, record)
    try:
        for entry in changes:
            path = Path(entry['path'])
            if fingerprint(path) != entry['before']:
                raise ValueError(f'Entry changed during installation: {path}')
            backup = backup_root / entry['relative']
            backup.parent.mkdir(parents=True, exist_ok=True)
            os.replace(path, backup)
            try:
                path.symlink_to(entry['target'], target_is_directory=True)
            except BaseException:
                os.replace(backup, path)
                raise
            record['entries'].append({**entry, 'backup': str(backup)})
            save(manifest, record)
        for entry in record['entries']:
            if Path(entry['path']).resolve() != Path(entry['target']):
                raise ValueError(f'Link verification failed: {entry["path"]}')
    except BaseException:
        # Roll back completed entries when they still belong to this operation.
        restore(manifest)
        raise
    return {'linked': len(record['entries']), 'backup': str(backup_root),
            'restore_manifest': str(manifest)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, default=Path.home(), help='Home root; override for isolated tests')
    parser.add_argument('--plan', type=Path, help='Write preview JSON, or read expected preview with --apply')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--restore', type=Path, help='Restore using a prior installation manifest')
    args = parser.parse_args()
    try:
        if args.restore:
            if args.apply or args.plan:
                parser.error('--restore cannot be combined with --apply or --plan')
            result = restore(args.restore)
        elif args.apply:
            if not args.plan:
                parser.error('--apply requires a previously inspected --plan')
            result = apply(args.home.resolve(), json.loads(args.plan.read_text()))
        else:
            result = plan(args.home.resolve())
            if args.plan:
                save(args.plan, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f'Skill linking failed: {error}\n')


if __name__ == '__main__':
    main()
