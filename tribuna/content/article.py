#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The Article content type."""

from plone.directives import form
from zope import schema
from five import grok
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import alsoProvides
from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView as View
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


class CommentsView(grok.View):
    grok.context(IArticle)
    grok.require('zope2.View')
    grok.name('comments-view')

    def get_comment_viewlet(self):
        request = self.request
        context = self.context

        # viewlet managers also require a view object for adaptation
        view = View(context, request)
        if not IViewView.providedBy(view):
            alsoProvides(view, IViewView)
        # finally, you need the name of the manager you want to find
        manager_name = 'plone.belowcontent'

        # viewlet managers are found by Multi-Adapter lookup
        manager = getMultiAdapter(
            (context, request, view), IViewletManager, manager_name)

        # calling update() on a manager causes it to set up its viewlets
        manager.update()
        return manager.viewlets[3].render()

    def get_addthis_viewlet(self):
        request = self.request
        context = self.context

        # viewlet managers also require a view object for adaptation
        view = View(context, request)
        if not IViewView.providedBy(view):
            alsoProvides(view, IViewView)
            # finally, you need the name of the manager you want to find
            manager_name = 'plone.belowcontentbody'

            # viewlet managers are found by Multi-Adapter lookup
            manager = getMultiAdapter(
                (context, request, view), IViewletManager, manager_name)

            # calling update() on a manager causes it to set up its viewlets
            manager.update()

            return manager.viewlets[-1].render()
