from setuptools import setup

setup(
    name="docstring_checker",
    version="0.1.0",
    py_modules=["check_docstrings"],
    install_requires=[],
    entry_points={
        "console_scripts": ["check-docstrings=check_docstrings:main"],
    },
)
