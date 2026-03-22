"""Setup script for gra-forum-app."""

from setuptools import setup, find_packages

setup(
    name="gra-forum-app",
    version="0.1.0",
    packages=find_packages(where=["backend", "cli"]),
    package_dir={"": "backend"},
    install_requires=[
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "openai>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "gra-software=cli.run_software_task:main",
        ],
    },
)