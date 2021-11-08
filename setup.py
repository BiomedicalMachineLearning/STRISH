from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup_requirements = []

setup(
    author="Genomics and Machine Learning lab",
    author_email="duy.pham@uq.edu.au",
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="A downstream analysis toolkit for Spatial Transcriptomic data",
    entry_points={
        "console_scripts": [
            "stlearn=stlearn.cli:main",
        ],
    },
    install_requires=requirements,
    license="BSD license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="STRISH",
    name="STRISH",
    packages=find_packages(include=["STRISH", "STRISH.*"]),
    setup_requires=setup_requirements,
    url="https://github.com/BiomedicalMachineLearning/STRISH",
    version="0.3.2",
    zip_safe=False,
)