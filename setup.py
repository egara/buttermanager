import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="buttermanager",
    version="2.4.1",
    author="Eloy García Almadén",
    author_email="eloy.garcia.pca@gmail.com",
    description="BTRFS tool for managing snapshots, balancing filesystems and upgrading the system safetly",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/egara/buttermanager",
    packages=['buttermanager', 'buttermanager.buttermanager', 'buttermanager.buttermanager.exception', 'buttermanager.buttermanager.filesystem', 'buttermanager.buttermanager.manager', 'buttermanager.buttermanager.util', 'buttermanager.buttermanager.window'],
    package_data= {'buttermanager.buttermanager': ['ui/*', 'images/*']},
    install_requires=[
       'PyQt5>=5.10.1',
       'PyYAML>=4.2b1',
    ],
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
    entry_points={
        "console_scripts": [
            "buttermanager = buttermanager.bm_main:main",
        ],
    },

)
