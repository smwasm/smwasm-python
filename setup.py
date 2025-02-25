from setuptools import setup, find_packages

PROJECT_URLS = {
   'Source Code': 'https://github.com/yaml/pyyaml',
}

setup(
    name="smwasm",
    version="0.0.4",
    author="smwasm",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.6",
    
    project_urls=PROJECT_URLS,
)
