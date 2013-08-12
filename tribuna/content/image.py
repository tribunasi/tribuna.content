from plone.directives import form
from zope import schema
from five import grok

from tribuna.content import _


class IImage(form.Schema):
    """Interface for Image content type."""

    title = schema.TextLine(
        title=_(u"Name"),
    )


class ImageView(grok.View):
    """View for displaying a comment (loaded with AJAX from mainpage)."""
    grok.context(IImage)
    grok.require('zope2.View')
    grok.name('image-view')
