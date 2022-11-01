from setuptools import setup, find_packages

import versioneer


setup(
    name="q2-SpiecEasi",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url="https://qiime2.org",
    #license="BSD-3-Clause",
    packages=find_packages(),
    author="Zakir Hossine, Isaac Towers and Benjamin Kaehler",
    author_email="zakirh@du.ac.bd, i.towers@adfa.edu.au; b.kaehler@adfa.edu.au",
    description="Apply spieceasi to generate adjagency matrix. ",
    scripts=['q2_SpiecEasi/assets/run_SpiecEasi.R'],
    package_data={
        'q2_SpiecEasi': ['assets/index.html'],
        'q2_SpiecEasi.tests': ['data/*']},
    entry_points={
        "qiime2.plugins":
        ["q2-SpiecEasi=q2_SpiecEasi.plugin_setup:plugin"]
    },
    zip_safe=False,
)