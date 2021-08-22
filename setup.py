from setuptools import setup, find_packages

setup(
    name='szu-autoconnect',
    packages=find_packages(),
    version='1.0.2',
    license='MIT',
    description='A simple way to get different DEXs abis for block chains.',
    author='Yong',
    author_email='ackness8@gmail.com',
    url='https://github.com/ackness/szu-autoconnect',
    keywords=['drcom', 'auto', 'SZU'],
    install_requires=[
        'PySimpleGUI',
        'apscheduler',
        'loguru',
        'retrying',
        'requests'
    ]
)
