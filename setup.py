#!/usr/bin/env python3

import os
from setuptools import setup, find_packages

package = "synth_crunch"

about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, package, '__version__.py')) as f:
    exec(f.read(), about)

def read_requirements(file_name):
    with open(file_name) as fd:
        return fd.read().splitlines()

with open('README.md') as fd:
    readme = fd.read()

setup(
    name=about['__title__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    version=about['__version__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        'infra': read_requirements("requirements.infra.txt"),
    },
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='package development template'
)
