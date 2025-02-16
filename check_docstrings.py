import ast
import sys
from pathlib import Path

def generate_docstring(func_node):
    """Generate a properly formatted docstring with dynamically sized underlines."""
    params = [arg.arg for arg in func_node.args.args]
    # Get the return annotation, if any; otherwise "None"
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

    insertions = []  # (position, text)
    removals = []    # (start_line, end_line)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check if the first statement in the function is a docstring.
            has_proper_docstring = (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(getattr(node.body[0], 'value', None), (ast.Str, ast.Constant))
            )
            if not has_proper_docstring:
                print(f"Fixing missing docstring for function `{node.name}` in {file_path}:{node.lineno}")
                new_docstring = generate_docstring(node)
                # If there is a body, insert before its first statement;
                # otherwise, insert right after the function definition.
                if node.body:
                    insert_position = node.body[0].lineno - 1
                else:
                    insert_position = node.lineno
                indentation = " " * (node.col_offset + 4)
                insertions.append((insert_position, f"{indentation}{new_docstring}\n"))
            else:
                # Remove any stray string literal expressions that are not the first statement.
                for stmt in node.body[1:]:
                    if isinstance(stmt, ast.Expr) and isinstance(getattr(stmt, 'value', None), (ast.Str, ast.Constant)):
                        # If available, use end_lineno to remove the whole block.
                        start = stmt.lineno - 1
                        end = getattr(stmt, "end_lineno", stmt.lineno)  # end_lineno is 1-indexed and inclusive
                        removals.append((start, end))
    
    # Apply removals in reverse order (so earlier removals don’t affect later line numbers).
    for start, end in sorted(removals, reverse=True):
        # Remove the block of lines; note: end is inclusive so we need to remove until end.
        del updated_lines[start:end]
    
    # Apply insertions in reverse order.
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
