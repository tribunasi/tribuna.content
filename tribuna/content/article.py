#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The Article content type."""

from five import grok
from plone.app.layout.globals.interfaces import IViewView
from plone.directives import form
from Products.Five.browser import BrowserView
from plone.namedfile.field import NamedBlobImage
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.viewlet.interfaces import IViewletManager

from tribuna.content import _


class IArticle(form.Schema):
    """Interface for Article content type."""

    title = schema.TextLine(
        title=_(u"Name"),
    )

    description = schema.Text(
        title=_(u"Article description"),
    )

    picture = NamedBlobImage(
        title=_(u"Image for main view"),
        required=False,
    )


class CommentsView(grok.View):
    """View for showing all the comments on the article and adding new
    comments.
    """

    grok.context(IArticle)
    grok.require('zope2.View')
    grok.name('comments-view')

    def get_comment_viewlet(self):
        """Method for getting comments viewlet so we can use it in
        other views"""

        request = self.request
        context = self.context

        # viewlet managers also require a view object for adaptation
        view = BrowserView(context, request)
        if not IViewView.providedBy(view):
            alsoProvides(view, IViewView)
        # finally, you need the name of the manager you want to find
        manager_name = 'plone.belowcontent'

        # viewlet managers are found by Multi-Adapter lookup
        manager = getMultiAdapter(
            (context, request, view), IViewletManager, manager_name)

        # calling update() on a manager causes it to set up its viewlets
        manager.update()
        all_viewlets = manager.viewlets
        for viewlet in all_viewlets:
            if viewlet.__name__ == u"plone.comments":
                return viewlet.render()


class View(grok.View):
    """Article view."""
    grok.context(IArticle)
    grok.require('zope2.View')
