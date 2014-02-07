# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from Products.CMFPlone.browser.interfaces import ISiteMap as \
    ISiteMapTheir
from redomino.advancedkeyword.browser.interfaces import \
    IRedominoAdvancedKeywordLayer


class ITribunaContentLayer(IRedominoAdvancedKeywordLayer):
    """Marker interface that defines a Zope 3 browser layer."""


class ISiteMap(ISiteMapTheir):
    """SiteMap interface."""
