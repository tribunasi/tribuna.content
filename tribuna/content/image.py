# -*- coding: utf-8 -*-

from plone.directives import form
from zope import schema
from five import grok

from tribuna.content import _
from tribuna.content.utils import tags_string_to_list


class IImage(form.Schema):
    """Interface for Image content type."""

    form.primary('title')
    title = schema.TextLine(
        title=_(u"Name"),
    )


class ImageView(grok.View):
    """View for displaying a comment (loaded with AJAX from mainpage)."""
    grok.context(IImage)
    grok.require('zope2.View')
    grok.name('image-view')

    def get_selected_tags(self):
        return tags_string_to_list(self.request.form.get('tags'))
