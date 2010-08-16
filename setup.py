#!/usr/bin/env python

from distutils.core import setup

f = open("README.rst")
long_description = f.read()
f.close()
f = open("CHANGELOG.rst")
long_description += f.read()
f.close()

setup(
    name="kong",
    version="0.2",
    description="Kongregate-related utilities",
    long_description=long_description,
    author="Corbin Simpson",
    author_email="MostAwesomeDude@gmail.com",
    url="http://github.com/MostAwesomeDude/kong",
    py_modules=["kong"],
    scripts=["scripts/kongregate"],
)
