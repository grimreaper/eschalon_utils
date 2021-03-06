from setuptools import setup

import eschalon

py2app_options = dict(
    argv_emulation=True,
    iconfile='data/eschalon1.icns',
)

setup(
    name='eschalon_utils',
    version=eschalon.version,
    packages=['eschalon'],
    url='http://apocalyptech.com/eschalon/',
    license='GPLv2+',
    author='CJ Kucera',
    author_email='cj@apocalyptech.com',
    description='Eschalon Books I, II, and III Character and Map Editors ',
    requires=[
        'Crypto',
        'gobject',
        'numpy',
        'pycrypto',
        'six',
        'bidict',
        'coloredlogs',
        'verboselogs',
        'vext',
        'vext.gi',
    ],
    scripts=[
        'eschalon/main.py',
    ],
    entry_points={
        'console_scripts': ['eschalon=main:main'],
    },
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'coverage',
        'parameterized',
        'xmlunittest',
        'nose-capturestderr',
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
    app=['eschalon/main.py'],
    options=dict(
        py2app=py2app_options,
    ),
    setup_requires=[
        'py2app',
        'isort'
    ],
)
