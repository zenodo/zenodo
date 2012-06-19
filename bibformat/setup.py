# -*- coding: utf-8 -*-

from setuptools import setup
from distutils.filelist import findall

setup(
    name='openaire-bibformat',
    version='0.1',
    packages=['invenio.bibformat_elements','invenio'],
    package_dir={'invenio': 'lib',},
    zip_safe=False,
    include_package_data=True,
    namespace_packages=['invenio','invenio.bibformat_elements'],
    data_files=[
        ('etc/bibformat/format_templates/', findall('format_templates/')),
        ('etc/bibformat/output_formats/', findall('output_formats/')),
    ],
)
