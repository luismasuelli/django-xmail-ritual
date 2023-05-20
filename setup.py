from setuptools import setup

setup(
    name='django-xmail-ritual',
    version='1.1.1',
    packages=[
        'grimoire.django.xmail',
        'grimoire.django.xmail.management',
        'grimoire.django.xmail.management.commands',
        'grimoire.django.xmail.migrations',
    ],
    package_data={
        'grimoire.django.xmail': [
            'locale/*/LC_MESSAGES/*.*'
        ]
    },
    url='https://github.com/luismasuelli/django-xmail-ritual',
    license='LGPL',
    author='Luis y Anita',
    author_email='luismasuelli@hotmail.com',
    description='The xmail library is a mail dispatching library for Django 2.2 or greater. Mails are sent asynchronously by a '
                'management command',
    install_requires=['python-cantrips>=1.0.0', 'Django>=4.2']
)
