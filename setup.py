from setuptools import setup, find_packages

setup(
    name="q2-SpiecEasi",
    version='0.0.0-dev',
    packages=find_packages(),
    author="Zakir Hossine, Isaac Towers, Ben Kaehler",
    description="Apply SpiecEasi to generate adjagency matrix.",
    license="BSD-3-Clause",
    url="https://github.com/BenKaehler/q2-SpiecEasi",
    entry_points={
        'qiime2.plugins': ['q2-SpiecEasi=q2_SpiecEasi.plugin_setup:plugin']
    },
    scripts=['q2_SpiecEasi/assets/run_SpiecEasi.R'],
    package_data={'q2_SpiecEasi': ['assets/*'],
                  'q2_SpiecEasi.tests': ['data/*']},
    zip_safe=False,
)
