from setuptools import (
    find_packages,
    setup,
)


setup(
    author='hey-mako',
    include_package_data=True,
    install_requires=[
        'Flask==1.0.2',
        'ansible==2.6.2',
        'celery==4.2.1',
        'pymongo==3.7.1',
        'redis==2.10.6',
    ],
    license='MIT',
    name='botops',
    packages=find_packages(
        exclude=[
            '*.tests',
            '*.tests.*',
            'tests',
            'tests.*',
        ]
    ),
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
    url='https://github.com/hey-mako/heroku-botops'
)
