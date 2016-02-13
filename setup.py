from setuptools import setup, find_packages

setup(
    name='django-modelforms',
    version='0.1.1',
    author='Touch Technology Pty Ltd',
    author_email='info@touchtechnology.com.au',
    maintainer='Gary Reynolds',
    maintainer_email='gary.reynolds@touchtechnology.com.au',
    description='Improvements to django.forms.ModelForm',
    license='BSD',
    install_requires=[
        'django>=1.7',
    ],
    packages=find_packages(),
)
