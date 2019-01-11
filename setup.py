from setuptools import setup, find_packages

setup(
    name='django-modelforms',
    version='0.3.0',
    author='Touch Technology Pty Ltd',
    author_email='info@touchtechnology.com.au',
    maintainer='Gary Reynolds',
    maintainer_email='gary.reynolds@touchtechnology.com.au',
    description='Improvements to django.forms.ModelForm',
    license='BSD',
    install_requires=[
        'django',
    ],
    packages=find_packages(),
)
