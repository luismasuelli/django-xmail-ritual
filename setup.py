from setuptools import setup, find_packages

setup(
    name='django-xmail-ritual',
    version='0.0.11',
    namespace_packages=['grimoire', 'grimoire.django'],
    packages=find_packages(exclude=['xmail_proj', 'xmail_proj.*']),
    package_data={
        'grimoire.django.xmail': [
            'locale/*/LC_MESSAGES/*.*'
        ]
    },
    url='https://github.com/luismasuelli/django-xmail-ritual',
    license='LGPL',
    author='Luis y Anita',
    author_email='luismasuelli@hotmail.com',
    description='The xmail library is a mail dispatching library for Django 1.7. Mails are sent asynchronously by a management command',
    install_requires=['python-cantrips>=0.6.6', 'Django>=1.7']
)