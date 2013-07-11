#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Views for the main page."""

from five import grok
from zope.interface import Interface


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
