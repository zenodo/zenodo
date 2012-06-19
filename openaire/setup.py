# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='openaire',
    version='0.1',
    packages=['invenio'],
    package_dir={'invenio': 'lib'},
    zip_safe=False,
    include_package_data=True,
    namespace_packages=['invenio'],
    data_files=[
        ('etc/', ['tpl/openaire_form.tpl', 'tpl/openaire_page.tpl']),
        ('lib/sql/openaire/', ['sql/tabcreate.sql',]),
        ('var/www/js/', ['js/openaire_deposit_engine.js',]),
    ],
)