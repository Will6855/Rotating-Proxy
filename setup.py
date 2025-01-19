from setuptools import setup, find_packages

setup(
    name='rotating_proxy',
    version='0.3.0',
    author='Will',
    author_email='',
    description='A Python package for managing and using rotating proxies',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Will6855/rotating-proxy',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Internet :: Proxy Servers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.9',
    install_requires=[
        'requests>=2.32.3',
        'typing>=3.7.4.3',
        'python-dateutil>=2.9.0',
        'urllib3>=2.2.1',
        'dataclasses>=0.8; python_version < "3.7"',
    ],
)
