import eschalon
from setuptools import setup

setup(
    name='eschalon_utils',
    version=eschalon.version,
    packages=['eschalon'],
    package_dir={'': ''},
    url='http://apocalyptech.com/eschalon/',
    license='GPLv2+',
    author='CJ Kucera',
    author_email='cj@apocalyptech.com',
    description='',
    requires=[
        'Crypto',
    ],
    extras_require={
        'gui': [
            'pygtk>=2.18.0',
            'gobject',
            'numpy',
        ],
        'map': [
            'czipfile',
            'pycrypto',
        ]

    },
    scripts=[
        'eschalon/main.py',
    ],
    entry_points={
        'console_scripts': ['eschalon=main:main'],
    },
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'coverage'
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: X11 Applications :: GTK',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Topic :: Games/Entertainment :: Role-Playing',
        'Topic :: Utilities',
    ],
)
