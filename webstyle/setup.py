# -*- coding: utf-8 -*-

from setuptools import setup
from distutils.filelist import findall, translate_pattern

css_pattern = translate_pattern("*.css", prefix="css")
png_pattern = translate_pattern("*.png", prefix="css")

setup(
    name='openaire-webstyle',
    version='0.1',
    packages=['invenio'],
    package_dir={'invenio': 'lib'},
    zip_safe=False,
    include_package_data=True,
    namespace_packages=['invenio'],
    data_files=[
        ('var/www/css/', filter( css_pattern.match, findall('css/'))),
        ('var/www/css/images/', filter( png_pattern.match, findall('css/'))),
        ('var/www/img/',findall('img/')),
        ('var/www/js/',findall('js/')),
        ('var/www/flash/',findall('flash/')),
    ],
)
