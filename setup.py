from setuptools import setup

setup(
    name='Logitech-G19-LCD-Driver',
    version='0.8',
    py_modules=['g19d' ],
    packages=['coloradapter', 'libdraw', 'logitech', 'appmgr'],
    package_dir={'libdraw': 'libdraw'},
    package_data={
        'libdraw': ['11676.otf']
    },
    entry_points={
        'console_scripts': [
            'g19d = g19d:main',
        ],
    }
)

