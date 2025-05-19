"""Setup configuration for the financial tools package.

This module defines the package metadata, dependencies, and entry points for
the financial tools system.
"""

from setuptools import setup

# Read the README file for the long description
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="financial_tools",
    version="0.1.0",
    author="William Prior",
    author_email="william.prior@example.com",
    description="A collection of financial tools and utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["financial_tools"],
    install_requires=[
        "boto3>=1.26.0",  # AWS SDK for Python
    ],
    entry_points={
        "console_scripts": [
            "financial-tools=financial_tools.cli.interface:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
)
