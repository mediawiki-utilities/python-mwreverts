import os

from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def requirements(fname):
    for line in open(os.path.join(os.path.dirname(__file__), fname)):
        yield line.strip()


setup(
    name="mwreverts",
    version="0.1.1",  # Change in mwreverts/__init__.py
    author="Aaron Halfaker",
    author_email="aaron.halfaker@gmail.com",
    url="http://github.com/mediawiki-utilities/python-mwreverts",
    packages=["mwreverts"],
    license=read("LICENSE"),
    description="A set of utilities for detecting reverts in MediaWiki " +
                "revisions.",
    long_description=read("README.md"),
    install_requires=requirements("requirements.txt"),
    setup_requires=['nose>=1.0', 'coverage']
)
