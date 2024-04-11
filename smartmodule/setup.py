from setuptools import setup, find_packages

setup(
    name = "smwasm",
    version = "0.0.1",

    # content information
    packages = find_packages(),

    include_package_data = True,

    # it exists as a directory, not as a .egg file
    zip_safe = False
    )
