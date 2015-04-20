from setuptools import setup, find_packages

setup(
    name='django-xmail-ritual',
    version='0.0.8',
    namespace_packages=['grimoire', 'grimoire.django'],
    packages=find_packages(),
    url='https://github.com/luismasuelli/django-xmail-ritual',
    license='LGPL',
    author='Luis y Anita',
    author_email='luismasuelli@hotmail.com',
    description='The xmail library is a mail dispatching library for Django 1.7. Mails are sent asynchronously by a management command',
    install_requires=['python-cantrips>=0.6.6', 'Django>=1.7']
)