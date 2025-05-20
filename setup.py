"""Setup configuration for the financial_tools package."""

from setuptools import find_packages, setup

setup(
    name="financial_tools",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.26.0",
    ],
    entry_points={
        "console_scripts": [
            "financial-tools=financial_tools.cli:main",
        ],
    },
    python_requires=">=3.8",
    author="William Prior",
    author_email="william.prior@example.com",  # Update this
    description="Financial tools for managing subscriptions, products, and goals",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/williamprior/pathway-builder-tools",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
