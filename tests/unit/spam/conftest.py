import pytest
from flask import current_app

@pytest.fixture
def use_safelist_config(app):
    """Activate webhooks config."""
    old_value_safelist_index = current_app.config.pop(
        'ZENODO_RECORDS_SAFELIST_INDEX_THRESHOLD')
    old_value_search_safelist = current_app.config.pop(
        'ZENODO_RECORDS_SEARCH_SAFELIST')

    current_app.config['ZENODO_RECORDS_SAFELIST_INDEX_THRESHOLD'] = 2
    current_app.config['ZENODO_RECORDS_SEARCH_SAFELIST'] = True

    yield
    current_app.config['ZENODO_RECORDS_SAFELIST_INDEX_THRESHOLD'] = \
        old_value_safelist_index
    current_app.config['ZENODO_RECORDS_SEARCH_SAFELIST'] = \
        old_value_search_safelist
