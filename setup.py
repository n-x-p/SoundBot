from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_text = f.read()

setup(
    name='SoundBot',
    version='0.0.1',
    description='Discord bot for playing music',
    long_description=readme,
    author='programmentry',
    author_email='n.x.peralta@gmail.com',
    url='https://github.com/n-x-p/SoundBot',
    license=license_text,
)
