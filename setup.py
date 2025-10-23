from setuptools import setup, find_packages

setup(
    name="Concode",
    version="0.1.0",
    packages=find_packages(include=["code_processor", "utils", "tests"]),
    install_requires=[
        # see requirements.txt at root and audio-to-text/requirements.txt
    ],
    entry_points={
        "console_scripts": [
            "concode=main:main",
        ]
    },
)
