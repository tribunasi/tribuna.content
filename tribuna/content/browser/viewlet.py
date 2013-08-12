#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Viewlets."""


from plone import api
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet

from tribuna.content.entrypage import View
from tribuna.content.homepage import HomePageView
from tribuna.content.mainpage import MainPageView
from tribuna.content.utils import get_articles


class NavbarViewlet(BrowserView):
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(NavbarViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request

    def update(self):
        pass

    def available(self):
        if isinstance(self.__parent__, View):
            return False
        return True

    def render(self):
        if self.available():
            root = api.portal.get_navigation_root(self.context).absolute_url()
            portal = api.portal.get()
            entry_pages = portal["entry-pages"]
            default_page = entry_pages[entry_pages.getDefaultPage()]
            return safe_unicode(navbar_template % (
                root,
                (root + '/++theme++tribuna.diazotheme/img/home.png'),
                (root + '/home-page'),
                (root + '/articles/++add++tribuna.content.article'),
                (root + '/tags/++add++tribuna.content.tag'),
                (root + '/images/createObject?type_name=Image'),
                (default_page.absolute_url() + "/edit"),
                (root + '/articles'),
                (root + '/tags'),
                (root + '/images')
                )
            )
        return ""


class DefaultSessionViewlet(BrowserView):
    """Method that checks our session to get
    the article we want to show first"""

    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(DefaultSessionViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request

    def update(self):
        pass

    def set_default_content_list(self, session):
        get_articles(session)

    def set_default_view_type(self, session):
        session.set('view_type', 'drag')

    def reset_session(self):
        """Check if we have the data, if we don't, initialize session
        parameters.
        """
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        get_default = self.request.get('default')
        if get_default and "portlet_data" in session.keys():
            del session["portlet_data"]
        if get_default or 'content_list' not in session.keys():
            self.set_default_content_list(session)
        if get_default or 'view_type' not in session.keys():
            self.set_default_view_type(session)

    def render(self):
        if (isinstance(self.__parent__, HomePageView)
                or isinstance(self.__parent__, MainPageView)):
            self.reset_session()
        return ""


navbar_template = u"""
<ul id="navbar-template">
    <li><a class="brand" href="%s"><img src="%s" alt="Home"/></a></li>
    <li><a href="%s">Home page</a></li>
    <li><a href="%s">Add article</a></li>
    <li><a href="%s">Add tag</a></li>
    <li><a href="%s">Add image</a></li>
    <li><a href="%s">Edit entry page</a></li>
    <li><a href="%s">Manage articles</a></li>
    <li><a href="%s">Manage tags</a></li>
    <li><a href="%s">Manage images</a></li>
</ul>
"""
