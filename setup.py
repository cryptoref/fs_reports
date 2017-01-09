"""
Create indexing reports for family search admins

"""
from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='fs_indexing_reports',
      version='0.1',
      description='Download Family Search indexing data and create reports for a specific LDS stake',
      long_description=readme(),
      url='http://github.com',
      author='David Grawrock',
      author_email='david_grawrock@hotmail.com',
      license='MIT',
      packages=['fs_reports'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.5',
          'Intended Audience :: Religion',
          'Natural Language :: English',
          'Topic :: Religion'
      ],
      keywords='familysearch reports indexing',
      install_requires=['pandas','numpy'],
      zip_safe=False)