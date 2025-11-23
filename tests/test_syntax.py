import subprocess

def test_syntax():
    result = subprocess.run(['flake8', '.'], capture_output=True, text=True)
    assert result.returncode == 0, f"Syntax errors or style issues found:\n{result.stdout}\n{result.stderr}"

test_syntax()