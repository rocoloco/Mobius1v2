"""
Deployment wrapper to handle Modal CLI encoding issues on Windows.
"""
import subprocess
import sys
import os

# Set UTF-8 encoding for subprocess
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'

try:
    # Run modal deploy
    result = subprocess.run(
        [sys.executable, '-m', 'modal', 'deploy', 'src/mobius/api/app_consolidated.py'],
        env=env,
        capture_output=True,
        text=True,
        errors='replace'  # Replace unencodable characters
    )

    # Print output (with encoding errors replaced)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        # Filter out the charmap encoding error
        for line in result.stderr.split('\n'):
            if 'charmap' not in line and 'codec' not in line:
                print(line, file=sys.stderr)

    sys.exit(result.returncode)

except Exception as e:
    print(f"Deployment failed: {e}", file=sys.stderr)
    sys.exit(1)
