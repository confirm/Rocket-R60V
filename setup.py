#!/usr/bin/env python
'''
Setup script to create a pip/pypi package via setuptools.
'''

from setuptools import setup, find_packages

with open('requirements-dev.txt') as f:
    requirements_dev = f.read().strip().split('\n')

setup(
    name='Rocket-R60V',
    use_scm_version=True,
    license='MIT',
    author='confirm IT solutions',
    description='Python API for the Rocket R 60V',
    long_description=open('README.rst').read(),
    url='https://github.com/confirm/Rocket-R60V',
    packages=find_packages(exclude=['tests']),
    scripts=[
        'rocket-r60v',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    setup_requires=[
        'setuptools_scm',
    ],
    extras_require={
        'develop': requirements_dev
    },

)
