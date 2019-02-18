# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import books_and_readers

setup(
    name='books_and_readers',
    version=books_and_readers.__version__,
    packages=find_packages(),
    author="Julien Laffargue",
    author_email="julien.laffargue@gmail.com",
    description="Answer to a recruitment technical exercise",
    long_description=open('README.md').read(),
    install_requires=["psycopg2", "boto3"],
    include_package_data=True,
    url='http://github.com/julaff/books_and_readers',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Topic :: Education",
    ]
)
