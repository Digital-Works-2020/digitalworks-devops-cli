from setuptools import setup, find_packages

setup(
    name="digitalworks-devops-cli",
    version="0.1.0",
    description="Unified DevOps CLI for Jira, AWS, and more.",
    author="Digitalworks2020",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'devops-cli=devops_cli.main:main',
        ],
    },
    license="MIT",
)
