import pytest
from flask import current_app

from zenodo.modules.metrics.api import ZenodoMetric


@pytest.fixture
def use_metrics_config(app):
    """Activate webhooks config."""
    old_value = current_app.config.pop('ZENODO_METRICS_DATA', None)
    current_app.config['ZENODO_METRICS_DATA'] = {
        'openaire-nexus': [
            {
                'name': 'zenodo_unique_visitors_web_total',
                'help': 'Number of unique visitors in total on Zenodo '
                        'portal',
                'type': 'gauge',
                'value': ZenodoMetric.get_visitors
            },
            {
                'name': 'zenodo_researchers_total',
                'help': 'Number of researchers registered on Zenodo',
                'type': 'gauge',
                'value': ZenodoMetric.get_researchers
            },
            {
                'name': 'zenodo_files_total',
                'help': 'Number of files hosted on Zenodo',
                'type': 'gauge',
                'value': ZenodoMetric.get_files
            },
            {
                'name': 'zenodo_communities_total',
                'help': 'Number of Zenodo communities created',
                'type': 'gauge',
                'value': ZenodoMetric.get_communities
            },
        ]
    }
    yield
    current_app.config['ZENODO_METRICS_DATA'] = old_value
