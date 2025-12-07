#!/usr/bin/env python3
"""Force deploy to Modal with proper encoding."""

import sys
import subprocess

# Set UTF-8 encoding for stdout/stderr
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    print("Deploying to Modal...")
    result = subprocess.run(
        ["modal", "deploy", "src/mobius/api/app_consolidated.py"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    # Print output, replacing problematic characters
    if result.stdout:
        print(result.stdout.replace('✓', '[OK]').replace('✗', '[FAIL]'))
    if result.stderr:
        print(result.stderr.replace('✓', '[OK]').replace('✗', '[FAIL]'), file=sys.stderr)

    if result.returncode == 0:
        print("\n[OK] Deployment successful!")
    else:
        print(f"\n[FAIL] Deployment failed with code {result.returncode}")

    sys.exit(result.returncode)

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
