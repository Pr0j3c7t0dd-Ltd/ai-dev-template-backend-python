"""Setup script for the package."""

from setuptools import find_packages, setup

setup(
    name="ai-dev-template-backend",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
)
