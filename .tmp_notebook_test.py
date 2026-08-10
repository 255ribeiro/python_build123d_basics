import sys
import traceback
from pathlib import Path

import nbformat
from nbclient import NotebookClient

root = Path('docs/tuto_colab_build')
notebooks = sorted(root.glob('*.ipynb'))
print(f'Found {len(notebooks)} notebooks')

passed = []
failed = []

for nb_path in notebooks:
    print(f'\n=== RUN {nb_path.as_posix()} ===')
    try:
        with nb_path.open('r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        client = NotebookClient(
            nb,
            timeout=180,
            kernel_name='python3',
            allow_errors=False,
            resources={'metadata': {'path': str(nb_path.parent)}}
        )
        client.execute()
        passed.append(nb_path.as_posix())
        print('PASS')
    except Exception as e:
        tb = traceback.format_exc()
        failed.append((nb_path.as_posix(), type(e).__name__, str(e), tb))
        print(f'FAIL: {type(e).__name__}: {e}')

print('\n=== SUMMARY ===')
print(f'PASSED {len(passed)}')
for p in passed:
    print(f'PASS|{p}')

print(f'FAILED {len(failed)}')
for p, et, em, tb in failed:
    print(f'FAIL|{p}|{et}|{em}')
    tail = '\n'.join([line for line in tb.splitlines() if line.strip()][-14:])
    print('TRACE_TAIL_START')
    print(tail)
    print('TRACE_TAIL_END')

if failed:
    sys.exit(1)
