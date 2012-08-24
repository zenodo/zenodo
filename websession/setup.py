# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='openaire-websession',
    version='0.1',
    packages=['invenio'],
    package_dir={'invenio': 'lib'},
    zip_safe=False,
    include_package_data=True,
    namespace_packages=['invenio'],
)