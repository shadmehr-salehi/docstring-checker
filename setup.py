from setuptools import setup

setup(
    name="docstring-checker",
    version="1",
    py_modules=["check_docstrings"],
    install_requires=[],
    entry_points={
        "console_scripts": ["check-docstrings=check_docstrings:main"],
    },
)
