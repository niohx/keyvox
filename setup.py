from setuptools import setup, find_packages

setup(
    name='keyvox',
    version='0.1',
    packages=find_packages(where='Lib'),
    package_dir={'': 'Lib'},
    install_requires=[
        'requests',
    ],
)