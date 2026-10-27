"""Relocate image/label paths in manifests without changing frozen algorithms."""
from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifests = [ROOT / 'data/course_full200/manifest.json']
    manifests += sorted((ROOT / 'results').glob('*/run_*/manifest.json'))
    changed = 0
    for manifest in manifests:
        if not manifest.is_file():
            continue
        data = json.loads(manifest.read_text(encoding='utf-8-sig'))
        records = data.get('records', [])
        count = 0
        for record in records:
            for key in ('image', 'reference'):
                old = record.get(key)
                if not isinstance(old, str):
                    continue
                normalized = old.replace('\\', '/')
                if '/data/' in normalized:
                    relative = 'data/' + normalized.split('/data/', 1)[1]
                elif normalized.startswith('data/'):
                    relative = normalized
                else:
                    continue
                target = ROOT / relative
                if not target.is_file():
                    raise FileNotFoundError(f'Missing input: {relative}')
                if old != str(target):
                    record[key] = str(target)
                    count += 1
        if count:
            backup = ROOT / 'tmp/original_manifests' / manifest.relative_to(ROOT)
            if not backup.exists():
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(manifest, backup)
            manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            changed += 1
            print(f'Relocated {count} input paths: {manifest.relative_to(ROOT)}')
    print(f'Complete: {changed} manifests changed; frozen sources and parameters unchanged.')


if __name__ == '__main__':
    main()
