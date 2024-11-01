from setuptools import setup, find_packages

setup(
	name='project1',
	version='1.0',
	author='Arpita Patnaik',
	authour_email='arpitapatnaik@ufl.com',
	packages=find_packages(exclude=('tests', 'docs')),
	setup_requires=['pytest-runner'],
	tests_require=['pytest']	
)