# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from tribuna.content.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of tribuna.content into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if tribuna.content is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('tribuna.content'))

    def test_uninstall(self):
        """Test if tribuna.content is cleanly uninstalled."""
        self.installer.uninstallProducts(['tribuna.content'])
        self.assertFalse(self.installer.isProductInstalled('tribuna.content'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ITribunaContentLayer is registered."""
        from tribuna.content.interfaces import ITribunaContentLayer
        from plone.browserlayer import utils
        self.failUnless(ITribunaContentLayer in utils.registered_layers())
