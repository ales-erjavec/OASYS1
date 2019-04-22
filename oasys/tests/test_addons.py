from unittest.mock import Mock
import pytest
from oasys.application.addons import is_updatable, Available, Installed, Installable


@pytest.mark.parametrize('items,expected', [
    (Available(installable=True), False),
    (Installed(installable=None, local=Mock()), False),
    (Installed(installable=Installable(name='mock_name',
                                       version='2.0.0',
                                       summary='mock_summary',
                                       description='mock_description',
                                       package_url='mock_package_url',
                                       release_urls='mock_release_urls'),
               local=Mock(version='1.0.0')), True),
])
def test_is_updatable(items, expected):
    assert is_updatable(items) == expected
