#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "Click>=6.0",
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]


setup(
    name="hirise_tools",
    version="0.7.0",
    description="Tools to work with MRO's HiRISE camera data.",
    long_description=readme + "\n\n" + history,
    author="K.-Michael Aye",
    author_email="kmichael.aye@gmail.com",
    url="https://github.com/michaelaye/pyrise",
    packages=["pyrise",],
    package_dir={"pyrise": "pyrise"},
    entry_points={
        "console_scripts": [
            "pyrise = pyrise.cli:main",
            "abrowse = pyrise.downloads:get_and_display_browse_product",
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="ISC license",
    zip_safe=False,
    keywords=["HiRISE", "MRO", "NASA", "PDS",],
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Topic :: Utilities",
    ],
    test_suite="tests",
    test_require=test_requirements,
)
