# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='openaire-bibsched',
    version='0.1',
    packages=['invenio','invenio.bibsched_tasklets'],
    package_dir={'invenio': 'lib'},
    include_package_data=True,
    zip_safe=False,
    namespace_packages=['invenio', 'invenio.bibsched_tasklets'],
)