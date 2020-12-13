from setuptools import setup, find_packages


setup(
    name="nginx-simple-login",
    version="0.1",
    packages=find_packages(include=['nslogin', 'nslogin.*']),
    author="Terry Geng",
    author_email="terry@terriex.com",
    description="",
    keywords="",
    platforms="any",
    install_requires=["flask", "pyyaml"],
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v2 "
        "or later (LGPLv2+)",
    ],
    entry_points={
        'console_scripts': [
            'nslogind=nslogin.nslogind:main',
            'nslogin-user=nslogin.nsloginuser:main'
        ]
    }
)
