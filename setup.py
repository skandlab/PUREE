from setuptools import find_packages, setup
setup(
    name='puree',
    packages=find_packages(),
    version='0.1.0',
    description='Puree offline usage API',
    author='SkanderupLab',
    license='MIT',
    install_requires=['requests']
)