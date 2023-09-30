from setuptools import find_packages, setup

setup(
    name="bspcpy",
    license = "MIT",
    author="AlanJS26",
    author_email="alanjoses.29@gmail.com",
    description="bspc wrapper for python",
    packages=find_packages(),
    url="https://github.com/AlanJs26/bspcpy",
    include_package_data=True,
    python_requires = ">=3.10"
)

