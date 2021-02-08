import setuptools
from irida_staramr_results.version import __version__

# Use the requirements file for install_requires on PyPi
install_requires = []
requirements = open("requirements.txt", "r")
for r in requirements:
    install_requires.append(r)

# Use the readme file as the long description on PyPi
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='irida-staramr-results',
    version=__version__,
    description='Exports StarAMR results available through IRIDA into a single report.',
    author='Marielle Manlulu',
    author_email='marielle.manlulu@canada.ca',
    url='https://github.com/phac-nml/irida-staramr-results',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license = 'Apache-2.0',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: Apache Software License",
    ],
    install_requires=install_requires,
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points = { 'console_scripts': ['irida_staramr_results=irida_staramr_results.cli:main']}
)