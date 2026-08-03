from setuptools import setup, find_packages

setup(
    name="pytab",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "pandas",
        "scipy",
        "matplotlib",
    ],
    python_requires='>=3.8',
)