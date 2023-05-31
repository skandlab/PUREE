from setuptools import find_packages, setup
setup(
    name='PUREE',
    packages=find_packages(),
    version='0.1.0',
    description='Puree offline usage API',
    author='SkanderupLab',
    license='MIT',
    install_requires=['requests==2.28.2', 'pandas==1.5.3']
)
