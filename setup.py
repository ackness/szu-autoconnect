from setuptools import setup, find_packages

setup(
    name='szu-autoconnect',
    packages=find_packages(include=['szu-autoconnect'], exclude=['build', 'dist']),
    package_dir={'szu-autoconnect': 'szu-autoconnect'},
    version='1.0.0',
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
