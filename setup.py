import os

from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-mav',
    version='0.1',
    packages=['mav'],
    include_package_data=True,
    license='BSD License',  # example license
    description='Implement Entity-Attribute-Value in Django without generic foreign keys.',
    long_description=README,
    url='http://www.example.com/',
    author='Dylan Verheul',
    author_email='dylan@zostera.nl',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
