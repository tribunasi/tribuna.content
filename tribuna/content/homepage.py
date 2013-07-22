#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Views for the home page."""

from five import grok
from plone import api
from zope.interface import Interface


class HomePageView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('home-page')

    def is_text_view(self):
        """Check if text view (this is the basic view) is selected.

        Read data from the session, if it isn't there, return True.
        """
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if('view_type' in session.keys()):
            if session['view_type'] == 'drag':
                return False
        return True

    def articles_union(self):
        """Return a catalog search result of articles that have the selected
        tag.
        """

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if('content_list' in session.keys()):
            return session['content_list']['union']
        return []

    def articles_intersection(self):
        """Return a catalog search result of articles that have the selected
        tag.
        """

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if('content_list' in session.keys()):
            return session['content_list']['intersection']
        return []

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

    def only_one_tag(self):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if('portlet_data' in session.keys()):
            return len(session['portlet_data']['tags']) == 1
        return False

    def tag_description(self):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)

        title = session['portlet_data']['tags'][0]
        with api.env.adopt_user('tags_user'):
            catalog = api.portal.get_tool(name='portal_catalog')
            tag = catalog(
                Title=title,
                portal_type='tribuna.content.tag',
            )[0].getObject()
        if not tag.description:
            return u"Description not added yet!"
        return tag.description

    def show_intersection(self):
        if self.only_one_tag() is True:
            return False
        if self.articles_intersection() == []:
            return False
        return True

    def show_union(self):
        if self.only_one_tag() is True:
            return False
        if self.articles_union() == []:
            return False
        return True
