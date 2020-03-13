from setuptools import setup

setup(
    name='solved-af',
    version='0.1',
    packages=['saf'],
    entry_points={
        'console_scripts': [
            'solved-af = saf.__main__:main'
        ]
    }
)
