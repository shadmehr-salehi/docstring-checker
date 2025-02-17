import ast
import sys
from pathlib import Path

def generate_docstring(func_node):
    """Generate a properly formatted docstring with dynamically sized underlines."""
    params = [arg.arg for arg in func_node.args.args]
    returns_annotation = (
        getattr(func_node.returns, "id", None)
        or getattr(func_node.returns, "attr", None)
        or "None"
    ) if func_node.returns else "None"

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

    insertions = []
    removals = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and not (node.name.startswith("_") and not node.name.startswith("__")):
            has_proper_docstring = (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(getattr(node.body[0], 'value', None), (ast.Str, ast.Constant))
            )
            if not has_proper_docstring:
                print(f"Fixing missing docstring for function `{node.name}` in {file_path}:{node.lineno}")
                new_docstring = generate_docstring(node)
                if node.body:
                    insert_position = node.body[0].lineno - 1
                else:
                    insert_position = node.lineno
                indentation = " " * (node.col_offset + 4)
                insertions.append((insert_position, f"{indentation}{new_docstring}\n"))
            else:
                for stmt in node.body[1:]:
                    if isinstance(stmt, ast.Expr) and isinstance(getattr(stmt, 'value', None), (ast.Str, ast.Constant)):
                        start = stmt.lineno - 1
                        end = getattr(stmt, "end_lineno", stmt.lineno)
                        removals.append((start, end))

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
    print("✅ Docstring checks complete. Misplaced docstrings were removed, and missing sections were added.")

if __name__ == "__main__":
    main()
