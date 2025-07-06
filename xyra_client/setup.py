from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xyra-client",
    version="0.1.0",
    author="Xyra Team",
    author_email="contact@xyra.com",
    description="Python SDK for the Xyra API - Track agent metrics across different billing models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/xyra",
    packages=find_packages(include=["xyra_client", "xyra_client.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.23.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=4.0.0",
            "mypy>=0.991",
        ],
        "examples": [
            "python-dotenv>=0.19.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/your-org/xyra/issues",
        "Source": "https://github.com/your-org/xyra",
        "Documentation": "https://docs.xyra.com",
    },
    keywords="xyra api sdk billing metrics tracking agent ai saas",
    include_package_data=True,
    zip_safe=False,
)