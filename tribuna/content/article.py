# -*- coding: utf-8 -*-
"""The Article content type."""

from plone.directives import form
from zope import schema

from tribuna.content import _


class IArticle(form.Schema):
    """Interface for Article content type."""

    title = schema.TextLine(
        title=_(u"Name"),
    )

    description = schema.Text(
        title=_(u"Article description"),
    )
