import os

from setuptools import find_packages, setup

about_path = os.path.join(os.path.dirname(__file__), "mwreverts/about.py")
exec(compile(open(about_path).read(), about_path, "exec"))


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def requirements(fname):
    for line in open(os.path.join(os.path.dirname(__file__), fname)):
        yield line.strip()

setup(
    name=__name__,  # noqa
    version=__version__,  # noqa
    author=__author__,  # noqa
    author_email=__author_email__,  # noqa
    description=__description__,  # noqa
    url=__url__,  # noqa
    license=__license__,  # noqa
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'mwreverts=mwreverts.mwreverts:main'
        ],
    },
    long_description=read("README.md"),
    install_requires=requirements("requirements.txt"),
    setup_requires=['nose>=1.0', 'coverage']
)
