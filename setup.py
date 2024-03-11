import os

from setuptools import find_packages, setup

setup(
    name="MATestbed",
    version="0.0.1",
    packages=find_packages(),
    install_requires=["numpy", "pandas", "lxml"],
    # Consider including this if you have a readme that's useful for developers or users within your organization
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
)
