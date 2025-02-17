import ast
import sys
from pathlib import Path

def generate_docstring(func_node, existing_docstring=None):
    """Generate a properly formatted docstring with dynamically sized underlines."""
    params = [arg.arg for arg in func_node.args.args]
    returns_annotation = (
        getattr(func_node.returns, "id", None)
        or getattr(func_node.returns, "attr", None)
        or "None"
    ) if func_node.returns else "None"

    description = existing_docstring if existing_docstring else f"{func_node.name.replace('_', ' ').capitalize()} function."
    docstring = '"""' + f"\n{description}\n\n"

    if params:
        docstring += "Args:\n" + "-" * len("Args") + "\n"
        for param in params:
            docstring += f"    {param} (TYPE): Description.\n"

    docstring += "\nReturns:\n" + "-" * len("Returns") + "\n"
    docstring += f"    {returns_annotation}: Description.\n"

    docstring += '\n"""'
    return docstring

def check_and_fix_docstrings(file_path):
    """Check and fix function docstrings in a given file."""
    with open(file_path, "r", encoding="utf-8") as file:
        source_code = file.readlines()

    tree = ast.parse("".join(source_code), filename=file_path)
    updated_lines = list(source_code)

    insertions = []
    removals = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and (not (node.name.startswith("_") or not node.name.startswith("__"))):
            has_proper_docstring = (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(getattr(node.body[0], 'value', None), (ast.Str, ast.Constant))
            )
            existing_docstring = None
            if has_proper_docstring:
                existing_docstring = node.body[0].value.s.strip()
                removals.append((node.body[0].lineno - 1, node.body[0].lineno))

            new_docstring = generate_docstring(node, existing_docstring)
            insert_position = node.body[0].lineno - 1 if has_proper_docstring else node.lineno
            indentation = " " * (node.col_offset + 4)
            insertions.append((insert_position, f"{indentation}{new_docstring}\n"))

    for start, end in sorted(removals, reverse=True):
        del updated_lines[start:end]

    for pos, text in sorted(insertions, reverse=True):
        updated_lines.insert(pos, text)

    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(updated_lines)

def main():
    """Main function to check and fix docstrings in Python files."""
    files_to_check = [Path(f) for f in sys.argv[1:] if f.endswith(".py")]
    for file in files_to_check:
        check_and_fix_docstrings(file)
    print("✅ Docstring checks complete. Misplaced or missing docstrings were fixed.")

if __name__ == "__main__":
    main()
