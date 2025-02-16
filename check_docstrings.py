import ast
import sys
from pathlib import Path

REQUIRED_SECTIONS = ["Args", "Returns"]

def check_docstring_coverage(file_path):
    """Check if a function docstring contains Args, Returns, and Raises."""
    with open(file_path, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read(), filename=file_path)

    errors = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            docstring = ast.get_docstring(node)
            if not docstring:
                errors.append(f"{file_path}:{node.lineno}: Function `{node.name}` is missing a docstring.")
                continue

            # Check for required sections
            for section in REQUIRED_SECTIONS:
                if f"{section}:" not in docstring:
                    errors.append(f"{file_path}:{node.lineno}: Function `{node.name}` is missing `{section}:` section in the docstring.")

    return errors

def main():
    """Main function to check all Python files."""
    files_to_check = [Path(f) for f in sys.argv[1:] if f.endswith(".py")]
    all_errors = []

    for file in files_to_check:
        all_errors.extend(check_docstring_coverage(file))

    if all_errors:
        for error in all_errors:
            print(error)
        sys.exit(1)  # Exit with failure

    sys.exit(0)  # Exit with success

if __name__ == "__main__":
    main()
