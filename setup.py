#!/usr/bin/env python

from pip.req import parse_requirements
from setuptools import setup


description = "Eventlet friendly profiler"

setup(
    name="eprofile",
    version="0.1",
    author="Brian Elliott",
    author_email="bdelliott@gmail.com",
    description=description,
    long_description=description,
    license="Apache",
    keywords="profiler tools",
    url="TBD",
    packages=['eprofile'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
    entry_points={
        'console_scripts': [
            'eprofile = eprofile.cli:main',
        ]
    }
)
