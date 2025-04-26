from setuptools import setup, find_packages

setup(
    name="advanced-port-scanner",
    version="1.0.0",
    description="A highly advanced modular port scanner and wireless attack tool",
    author="morningstar",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    python_requires='>=3.7',
)
