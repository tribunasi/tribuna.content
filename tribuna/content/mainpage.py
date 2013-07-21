#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Views for the main page."""

from five import grok
from zope.interface import Interface
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import alsoProvides
from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView as View
from zope.viewlet.interfaces import IViewletManager


class MainPageView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('main-page')

    def articles_all(self):
        """Return a catalog search result of articles that have the selected
        tag.
        """

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if('content_list' in session.keys()):
            return(session['content_list']['intersection'] +
                   session['content_list']['union'])
        return []

    def update(self):
        super(MainPageView, self).update()
        self.request.set('disable_plone.rightcolumn', 1)
        self.request.set('disable_plone.leftcolumn', 1)
        self.request.set('disable_border', 1)

    def get_comment_viewlet(self, context):
        request = self.request

        # viewlet managers also require a view object for adaptation
        view = View(context, request)
        if not IViewView.providedBy(view):
            alsoProvides(view, IViewView)
        # finally, you need the name of the manager you want to find
        manager_name = 'plone.belowcontent'

        # viewlet managers are found by Multi-Adapter lookup
        manager = getMultiAdapter((context, request, view), IViewletManager, manager_name)

        # calling update() on a manager causes it to set up its viewlets
        manager.update()
        return manager.viewlets[3].render()
