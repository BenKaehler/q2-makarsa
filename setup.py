from setuptools import find_packages, setup

setup(
    name="q2-makarsa",
    version="0.0.0-dev",
    packages=find_packages(),
    author="Zakir Hossine, Isaac Towers, Ben Kaehler",
    description="Build webs, maybe understand microbiomes.",
    license="BSD-3-Clause",
    url="https://github.com/BenKaehler/q2-makarsa",
    entry_points={
        "qiime2.plugins": ["q2-makarsa=q2_makarsa.plugin_setup:plugin"]
    },
    scripts=["q2_makarsa/assets/run_SpiecEasi.R"],
    package_data={
        "q2_makarsa": ["assets/*", "assets/assets/*/*"],
        "q2_makarsa.tests": ["data/*"],
    },
    zip_safe=False,
)
