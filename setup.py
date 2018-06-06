from setuptools import (
	find_packages,
	setup,
)


setup(
	author='hey-mako',
	include_package_data=True,
	install_requires=[
		'Flask==1.0.2',
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
