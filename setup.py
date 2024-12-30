import os
import subprocess
import shutil
from setuptools import setup, find_packages

def check_dependencies():
    """Check if QEMU and GDB are installed."""
    missing = []
    for tool in ['qemu-system-x86_64', 'gdb']:
        if not shutil.which(tool):
            missing.append(tool)
    if missing:
        raise RuntimeError(f"Missing required tools: {', '.join(missing)}. Please install them and try again.")

# Run the dependency check
try:
    check_dependencies()
except RuntimeError as e:
    print(str(e))
    exit(1)


# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="ezqm",
    version="1.0.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=["ezqm","ezqm.ezlib"]),
    install_requires=[line.strip() for line in open("requirements.txt")],
    entry_points={
        'console_scripts': [
            'ezcf=ezqm.ezcf:main',
            'ezgdb=ezqm.ezgdb:main',
            'ezqm=ezqm.ezqm:main',
            'ezcp=ezqm.ezcp:main',
        ]
    },
)
