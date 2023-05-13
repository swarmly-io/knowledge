from setuptools import setup, find_packages
import os
build_num = os.getenv("GITHUB_RUN_NUMBER") or '0'

setup(
    name='s_knowledge',
    version='0.1.0.' + build_num,
    description='Knowledge extraction',
    author='Adrian Plani',
    author_email='adrian@swarmly.io',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)