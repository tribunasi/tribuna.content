#!/usr/bin/env python
# -*- coding: utf-8 -*-

from persistent import Persistent
from plone.app.discussion.browser.comments import CommentForm
from plone.z3cform.fieldsets import extensible
from tribuna.content.comment import Comment
from z3c.form.field import Fields
from zope import interface
from zope import schema
from zope.annotation import factory
from zope.component import adapts
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICommentExtenderFields(Interface):
    """Interface to define the fields we want to add to the comment form."""
    subject = schema.List(
        title=(u"Tags"),
        value_type=schema.TextLine(),
        default=[],
        required=False
    )


class CommentExtenderFields(Persistent):
    """Persistent class that implements the ICommentExtenderFields interface.
    """
    interface.implements(ICommentExtenderFields)
    adapts(Comment)
    subject = u""


# CommentExtenderFields factory
CommentExtenderFactory = factory(CommentExtenderFields)


class CommentExtender(extensible.FormExtender):
    """Extending the comment form with the fields defined in the
    ICommentExtenderFields interface.
    """
    adapts(Interface, IDefaultBrowserLayer, CommentForm)

    fields = Fields(ICommentExtenderFields)

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form

    def update(self):
        # Add the fields defined in ICommentExtenderFields to the form.
        self.add(ICommentExtenderFields, prefix="")
