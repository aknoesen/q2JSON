from setuptools import setup, find_packages

setup(
    name="q2validate",
    version="0.1.0",
    description="JSON validation tool for Q2LMS instructor workflow",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.28.0",
        "pandas>=2.0.0", 
        "jsonschema>=4.0.0",
    ],
    python_requires=">=3.8",
)
