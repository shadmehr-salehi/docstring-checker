import ast
import sys
from pathlib import Path

REQUIRED_SECTIONS = ["Args", "Returns", "Raises"]

def generate_docstring(func_node):
    """Generate a formatted docstring with dynamically sized underlines."""
    params = [arg.arg for arg in func_node.args.args]
    returns_annotation = getattr(func_node.returns, "id", "None") if func_node.returns else "None"

    docstring = '"""' + f"\n{func_node.name.replace('_', ' ').capitalize()}.\n\n"

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

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            docstring = ast.get_docstring(node)
            if not docstring:
                print(f"Fixing missing docstring for function `{node.name}` in {file_path}:{node.lineno}")
                new_docstring = generate_docstring(node)

                # Insert new docstring after function definition
                insert_position = node.body[0].lineno - 1 if node.body else node.lineno
                updated_lines.insert(insert_position, f'    {new_docstring}\n\n')

    # Write back the updated content
    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(updated_lines)

def main():
    """Main function to check and fix docstrings in Python files."""
    files_to_check = [Path(f) for f in sys.argv[1:] if f.endswith(".py")]

    for file in files_to_check:
        check_and_fix_docstrings(file)

    print("✅ Docstring checks complete. Missing sections have been added.")

if __name__ == "__main__":
    main()
