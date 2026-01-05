import shutil
import subprocess
import sys


def check_command(name: str, command: list [str], expected_in_output: str = "") -> bool:
    """Check if a command exists and runs successfully"""
    print(f"Checking {name}...", end =" ")
    
    path = shutil.which(command[0])
    if not path:
        print(f"❌ {command[0]} not found in PATH")
        return False
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if expected_in_output and expected_in_output not in result.stdout + result.stderr:
            print("❌ Unexpected output")
            return False
        print(f"✅ Found at {path}")
        return True
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def check_python_version() -> bool:
    """Verify Python version is 3.12+."""
    print("Checking Python version...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 12:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    print(f"❌ Python {version.major}.{version.minor} (need 3.12+)")
    return False


def check_git_config() -> bool:
    """Verify Git is configured with name and email."""
    print("Checking Git configuration...", end=" ")
    try:
        name = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
        )
        email = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True,
            text=True,
        )
        if name.stdout.strip() and email.stdout.strip():
            print(f"✅ {name.stdout.strip()} <{email.stdout.strip()}>")
            return True
        print("❌ Name or email not configured")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main() -> int:
    """Run all environment checks."""
    print("=" * 60)
    print("Django Mentorship - Environment Verification")
    print("=" * 60)
    print()

    checks = [
        ("Python Version", check_python_version),
        ("uv", lambda: check_command("uv", ["uv", "--version"])),
        ("Git", lambda: check_command("git", ["git", "--version"])),
        ("Git Config", check_git_config),
        ("ruff", lambda: check_command("ruff", ["uv", "run", "ruff", "--version"])),
        ("pytest", lambda: check_command("pytest", ["uv", "run", "pytest", "--version"])),
    ]

    results = []
    for name, check_func in checks:
        results.append(check_func())

    print()
    print("=" * 60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ All checks passed! ({passed}/{total})")
        print("Your environment is ready for Django development.")
        return 0
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("Please fix the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())