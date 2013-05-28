"""Module where all interfaces, events and exceptions live."""

from plone.theme.interfaces import IDefaultPloneLayer
from redomino.advancedkeyword.browser.interfaces import IRedominoAdvancedKeywordLayer

class ITribunaContentLayer(IRedominoAdvancedKeywordLayer):
    """Marker interface that defines a Zope 3 browser layer."""
