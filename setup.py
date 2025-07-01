import os
import subprocess
import shutil
from setuptools import setup, find_packages


# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="ezqm",
    version="1.0.2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=["ezqm", "ezqm.ezlib"]),
    install_requires=["pexpect"],
    entry_points={
        'console_scripts': [
            'ezcf=ezqm.ezcf:main',
            'ezgdb=ezqm.ezgdb:main',
            'ezqm=ezqm.ezqm:main',
            'ezcp=ezqm.ezcp:main',
        ]
    },
)
