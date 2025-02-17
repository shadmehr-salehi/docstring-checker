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

    # Use existing docstring if present; otherwise, create a simple placeholder description.
    description = existing_docstring or f"{func_node.name.replace('_', ' ').capitalize()} function."
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
        # 1) Must be a FunctionDef
        # 2) Skip if name starts with '_' (private) or is a magic method (starts and ends with '__')
        if (
            isinstance(node, ast.FunctionDef)
            and not (
                node.name.startswith('_')  # private methods
                or (node.name.startswith('__') and node.name.endswith('__'))  # magic/dunder
            )
        ):
            # Check if the first body statement is a string (docstring)
            first_body_item = node.body[0] if node.body else None
            has_proper_docstring = (
                first_body_item
                and isinstance(first_body_item, ast.Expr)
                and isinstance(getattr(first_body_item, 'value', None), (ast.Str, ast.Constant))
            )

            existing_docstring = None
            if has_proper_docstring:
                # Extract the existing docstring text
                existing_docstring = first_body_item.value.s.strip()

                # Remove all lines of the docstring from source
                # (We use end_lineno to handle multi-line docstrings properly)
                removals.append((first_body_item.lineno - 1, first_body_item.end_lineno))

            # Generate the new docstring text (or reuse existing text)
            new_docstring = generate_docstring(node, existing_docstring)

            # Decide where to insert the new docstring
            insert_position = (
                first_body_item.lineno - 1 if has_proper_docstring
                else node.lineno
            )

            # Indent the docstring to match the function’s body
            indentation = " " * (node.col_offset + 4)
            insertions.append((insert_position, f"{indentation}{new_docstring}\n"))

    # Apply removals in reverse order
    for start, end in sorted(removals, reverse=True):
        del updated_lines[start:end]

    # Apply insertions in reverse order
    for pos, text in sorted(insertions, reverse=True):
        updated_lines.insert(pos, text)

    # Overwrite the file with the modified source
    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(updated_lines)

def main():
    """Main function to check and fix docstrings in Python files."""
    files_to_check = [Path(f) for f in sys.argv[1:] if f.endswith(".py")]
    for file in files_to_check:
        check_and_fix_docstrings(file)
    print("✅ Docstring checks complete. Private and magic methods were skipped.")

if __name__ == "__main__":
    main()
