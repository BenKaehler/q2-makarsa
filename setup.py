from setuptools import setup, find_packages

setup(
    name="pretty-easi",
    version='0.0.0-dev',
    packages=find_packages(),
    author="Zakir Hossine, Ben Kaehler, Isaac Towers",
    description="Apply SpiecEasi to generate adjagency matrix.",
    license="BSD-3-Clause",
    url="https://github.com/BenKaehler/pretty-easi",
    entry_points={
        'qiime2.plugins': ['pretty-easi=pretty_easi.plugin_setup:plugin']
    },
    scripts=['pretty_easi/assets/run_SpiecEasi.R'],
    package_data={'pretty_easi': ['assets/*', 'assets/assets/*/*'],
                  'pretty_easi.tests': ['data/*']},
    zip_safe=False,
)
