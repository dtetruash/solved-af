from setuptools import setup

setup(
    name = 'saf',
    version = '0.1',
    packages = ['saf'],
    entry_points = {
        'console_scripts': [
            'saf = saf.__main__:main'
        ]
    }
)