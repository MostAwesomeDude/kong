#!/usr/bin/env python

from distutils.core import setup

setup(
    name="kong",
    version="0.1",
    description="Kongregate-related utilities",
    author="Corbin Simpson",
    author_email="MostAwesomeDude@gmail.com",
    url="http://github.com/MostAwesomeDude/kong",
    py_modules=["kong"],
    scripts=["scripts/kongregate"],
)
