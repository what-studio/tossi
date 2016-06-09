# -*- coding: utf-8 -*-
import os

from setuptools import find_packages, setup


# Include __about__.py.
__dir__ = os.path.dirname(__file__)
about = {}
with open(os.path.join(__dir__, 'tossi', '__about__.py')) as f:
    exec(f.read(), about)


setup(
    name='tossi',
    version=about['__version__'],
    license=about['__license__'],
    author=about['__author__'],
    maintainer=about['__maintainer__'],
    maintainer_email=about['__maintainer_email__'],
    url='https://github.com/what-studio/tossi',
    description='Supports Korean particles',
    platforms='any',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: Korean',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Localization',
        'Topic :: Text Processing :: Linguistic',
    ],
    install_requires=['bidict', 'six'],
)
