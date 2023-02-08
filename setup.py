#!/usr/bin/env python
#from setuptools import setup

# from distutils.core import setup

from distutils.core import setup
import os,glob,sys
config = dict(
	name='pype',
	version = '0.0.6',
    packages=['pype'],
	include_package_data=True,
	license='MIT',
	author='Feng Geng',
	author_email='shouldsee@qq.com',
	long_description=open('README.md').read(),
	# python_requires = '>=3.6',
	classifiers = [
	'Programming Language :: Python :: 3.5',
	'Programming Language :: Python :: 3.7',
	],
	install_requires=[
		'toml',
		'pyyaml','pydantic-yaml','prettytable','pydantic',
	        'filelock',
		'namedlist',
		'parso','tqdm'
         #'typeguard',
		# x.strip() for x in open("requirements.txt","r")
        # 	if x.strip() and not x.strip().startswith("#")
	],
    extras_require = {
        'testing':  ['pytest',]
    },
    entry_points={
        "console_scripts": [
            # "pyluck=luck.cli:luck_main",
            # "pyluckmake=luck.luck_build_main:luck_build_main",
            ]},

)

	# assert sys.version_info >= (3,5),('Requires python>=3.5, found python==%s'%('.'.join([str(x) for x in sys.version_info[:3]])))
setup(**config)

# if __name__ == '__main__':
