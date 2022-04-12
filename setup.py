from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

with open("README.md", encoding="utf8") as readme_file:
    readme = readme_file.read()

setup_requirements = []

setup(
    author="Genomics and Machine Learning lab",
    author_email="uqmtra12@uq.edu.au",
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
    description="Spatial TRanscriptomic In Situ Hybridization (STRISH)",
    install_requires=requirements,
    license="BSD license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="STRISH",
    name="STRISH",
    packages=find_packages(include=["STRISH_test", "STRISH.*"]),
    setup_requires=setup_requirements,
    url="https://github.com/minhtran1309/STRISH",
    version="0.2.0",
    zip_safe=False,
)
