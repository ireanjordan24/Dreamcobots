import os
import sys

REQUIRED_FILES = [
    ["config.json"],
    ["main.py", "index.js"],
    ["metrics.py", "metrics.js"],
    ["README.md"],
]


def is_bot_folder(path):
    return any(name.lower().endswith("bot") for name in path.split(os.sep))


def validate_bot(bot_path):
    files = os.listdir(bot_path)
    errors = []

    for group in REQUIRED_FILES:
        if not any(f in files for f in group):
            errors.append(f"Missing one of: {group}")

    return errors


def scan_repo():
    failed = False

    for root, dirs, files in os.walk("."):
        if is_bot_folder(root):
            errors = validate_bot(root)

            if errors:
                failed = True
                print(f"\n❌ Bot failed: {root}")
                for e in errors:
                    print(f"   - {e}")
            else:
                print(f"✅ Bot passed: {root}")

    return failed


if __name__ == "__main__":
    failed = scan_repo()
    if failed:
        print("\n🚨 BOT VALIDATION FAILED")
        sys.exit(1)
    else:
        print("\n🔥 ALL BOTS VALID")
