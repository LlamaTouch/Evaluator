import os
from setuptools import find_packages, setup


def parse_requirements(require_path: str = "requirements.txt"):
    with open(require_path, "r") as f:
        lines = f.readlines()
    requirements = [
        line.strip() for line in lines if line.strip() and not line.startswith("#")
    ]
    return requirements


if __name__ == "__main__":
    setup(
        name="evaluator",
        version="0.0.1",
        packages=find_packages(exclude=()),
        include_package_data=True,
        python_requires=">=3.7",
        url="https://github.com/MaTestbed/Evaluator",
        # author="",
        # author_email="",
        # license="",
        install_requires=parse_requirements(),
    )
