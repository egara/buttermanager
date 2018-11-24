import setuptools
import pip

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

links = []
requires = []

try:
    requirements = pip.req.parse_requirements('requirements.txt')
except:
    # new versions of pip requires a session
    requirements = pip.req.parse_requirements(
        'requirements.txt', session=pip.download.PipSession())

for item in requirements:
    # we want to handle package names and also repo urls
    if getattr(item, 'url', None):  # older pip has url
        links.append(str(item.url))
    if getattr(item, 'link', None): # newer pip has link
        links.append(str(item.link))
    if item.req:
        requires.append(str(item.req))

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="buttermanager",
    version="1.0",
    author="Eloy García Almadén",
    author_email="eloy.garcia.pca@gmail.com",
    description="BTRFS tool for managing snapshots, balancing filesystems and upgrading the system safetly",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/egara/buttermanager",
    packages=setuptools.find_packages(),
    install_requires=requires
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Filesystems",
        "Topic :: Utilities"
    ],
)
