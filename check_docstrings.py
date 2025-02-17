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

    # Use the existing docstring if present; otherwise, create placeholder text
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
        # 2) Skip if name starts with '_' (private) or is a magic method (dunder)
        if (
            isinstance(node, ast.FunctionDef)
            and not (
                node.name.startswith('_')  # private method
                or (node.name.startswith('__') and node.name.endswith('__'))  # magic
            )
        ):
            first_body_item = node.body[0] if node.body else None
            
            # Check if the first body statement is actually a docstring
            has_proper_docstring = (
                first_body_item
                and isinstance(first_body_item, ast.Expr)
                and isinstance(getattr(first_body_item, 'value', None), (ast.Str, ast.Constant))
            )
            
            existing_docstring = None
            if has_proper_docstring:
                # Extract the existing docstring text
                existing_docstring = first_body_item.value.s.strip()
                
                # Remove ALL lines occupied by the original docstring
                # Note: end_lineno is inclusive, so we do (+1) in the slice to remove that line too
                start_line = first_body_item.lineno - 1  # -1 because list is 0-based vs AST is 1-based
                end_line = first_body_item.end_lineno
                removals.append((start_line, end_line + 1))

            # Generate a new docstring (either from existing text or a placeholder)
            new_docstring = generate_docstring(node, existing_docstring)

            # Decide where to insert the new docstring
            # If we had a docstring, insert at the old docstring's start line
            # Otherwise, insert right after the function definition line
            insert_position = (
                first_body_item.lineno - 1 if has_proper_docstring
                else node.lineno
            )

            # Indent the docstring to match function body
            indentation = " " * (node.col_offset + 4)
            insertions.append((insert_position, f"{indentation}{new_docstring}\n"))

    # Apply removals in reverse
    for start, end in sorted(removals, reverse=True):
        del updated_lines[start:end]

    # Apply insertions in reverse
    for pos, text in sorted(insertions, reverse=True):
        updated_lines.insert(pos, text)

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
