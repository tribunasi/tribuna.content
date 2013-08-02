#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Views for the main page."""

from five import grok
from plone import api
from zope.interface import Interface


from tribuna.content.portlets.sidebar import articles


class MainPageView(grok.View):
    """Mainpage view that shows all our articles in gallery view"""

    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('main-page')

    def articles_all(self):
        """Return a catalog search result of articles that have the selected
        tag.
        """

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        get_article = self.request.get('article')
        all_articles = articles(session)
        full_session = all_articles[0] + all_articles[1]
        if get_article in [i.id for i in full_session]:
            return full_session
        else:
            catalog = api.portal.get_tool(name='portal_catalog')
            return [catalog(id=get_article)[0].getObject()]
        return []

    def update(self):
        """Disabling plone columns that we don't want here"""

        super(MainPageView, self).update()
        self.request.set('disable_plone.rightcolumn', 1)
        self.request.set('disable_plone.leftcolumn', 1)
        self.request.set('disable_border', 1)
