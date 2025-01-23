from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()
    print(required)

setup(
    name="openspecy_python_interface",
    version="1.0.1",
    description="""This package is designed to easily interface with the OpenSpecy package for R. Python is used for file preprocessing and post-processing, and OpenSpecy is accessed by executing R from Python.""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kristopher Heath",
    packages=find_packages(include=["openspecy"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=required,
    license="MIT",
    url="https://github.com/KrisHeathNREL/OpenSpecy-Python-Interface",
)