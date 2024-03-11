import os

from setuptools import find_packages, setup

setup(
    name="matestbed",
    version="0.0.1",
    packages=find_packages(include=["evaluator.*"]),
    install_requires=["numpy", "pandas", "lxml"],
)
