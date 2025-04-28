from setuptools import setup, find_packages

setup(
    name="xyra-client",
    version="0.1.0",
    description="Python SDK for the Xyra API",
    packages=find_packages(include=["xyra_client", "xyra_client.*"]),
    install_requires=["httpx>=0.23.0"],
    python_requires=">=3.8",
)