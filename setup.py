import setuptools
from irida_staramr_results.version import __version__

install_requires = []
requirements = open("requirements.txt", "r")
for r in requirements:
    install_requires.append(r)

setuptools.setup(
    name='irida-staramr-results',
    version=__version__,
    description='Exports StarAMR results available through IRIDA into a single report.',
    author='Marielle Manlulu',
    author_email='marielle.manlulu@canada.ca',
    url='https://github.com/phac-nml/irida-staramr-results',
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
    include_package_data=True
)