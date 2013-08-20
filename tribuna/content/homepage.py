#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Views for the home page."""

from five import grok
from mobile.sniffer.detect import detect_mobile_browser
from mobile.sniffer.utilities import get_user_agent
from plone import api
from plone.app.search.browser import quote_chars
from Products.Five.browser import BrowserView
from zope.interface import Interface

from tribuna.content import _
from tribuna.content.utils import get_articles
from tribuna.content.utils import reset_session


def search_articles(query, session):
    """Method for getting correct search results

    :param query: Text that we search for
    :type query: string
    :param session: Current session
    :type session: Session getObject
    """
    if 'search-view' not in session.keys():
        return
    session['search-view']["active"] = True
    session['search-view']['query'] = query
    if "portlet_data" in session.keys():
        session["portlet_data"]["tags"] = []


class SearchView(BrowserView):
    """View that handles the searching and then redirects to the home page
    to display the results.

    This overrides the default Plone @@search view.
    """

    def __call__(self):
        query = quote_chars(self.request.form.get('SearchableText', ''))
        if query:
            query = query + '*'
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        search_articles(query, session)
        url = api.portal.get().absolute_url()
        self.request.response.redirect("{0}/home".format(url))


class HomePageView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('home')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.context.session_data_manager.getSessionData(
            create=True)
        self.articles = self._get_articles()
        super(HomePageView, self).__init__(context, request)

    def set_default_view_type(self, session):
        session.set('view_type', 'drag')

    def set_default_filters(self, session):
        session.set('portlet_data', {
            'all_tags': [],
            'tags': [],
            'sort_on': 'latest',
            'content_filters': ['article', 'comment', 'image']
        })

    def check_if_default(self):
        get_default = self.request.get('default')
        reset_session(self.session, get_default)

    def is_text_view(self):
        """Check if text view (this is the basic view) is selected.

        Read data from the session, if it isn't there, return True.
        """
        # Get HTTP_USER_AGENT from HTTP request object
        ua = get_user_agent(self.request)
        if ua and detect_mobile_browser(ua):
            # Redirect the visitor from a web site to a mobile site
            True
        elif 'view_type' in self.session.keys():
            if self.session['view_type'] == 'drag':
                return False
        return True

    def _get_articles(self):
        """Return all articles for the given query."""
        # XXX: The viewlet takes care of that, we should either move everything
        # here or leave everything there
        self.check_if_default()
        articles_all = get_articles(self.session)
        return {
            'intersection': articles_all[0],
            'union': articles_all[1],
            'all': articles_all[0] + articles_all[1]
        }

    def only_one_tag(self):
        if 'portlet_data' in self.session.keys():
            return len(self.session['portlet_data']['tags']) == 1
        return False

    def tag_text(self):
        title = self.session['portlet_data']['tags'][0]
        with api.env.adopt_user('tags_user'):
            catalog = api.portal.get_tool(name='portal_catalog')
            tag = catalog(
                Title=title,
                portal_type='tribuna.content.tag',
            )[0].getObject()
        if not tag.text:
            return _(u"Description not added yet!")
        return tag.text

    def tag_picture(self):
        title = self.session['portlet_data']['tags'][0]
        with api.env.adopt_user('tags_user'):
            catalog = api.portal.get_tool(name='portal_catalog')
            tag = catalog(
                Title=title,
                portal_type='tribuna.content.tag',
            )[0].getObject()
        if not hasattr(tag, 'image') or not tag.image:
            return None
        return str(tag.absolute_url()) + "/@@images/image"

    def is_search_view(self):
        if ("search-view" in self.session.keys() and
                self.session["search-view"]["active"]):
            return True
        return False

    def show_intersection(self):
        if (self.only_one_tag() or
            self.articles["intersection"] == [] or
                self.is_search_view()):
            return False
        return True

    def show_union(self):
        if (self.only_one_tag() or
            self.articles["union"] == [] or
                self.is_search_view()):
            return False
        return True

    def shorten_text(self, text):
        if len(text) > 140:
            return text[:140] + ' ...'
        return text

    def entry_page_edit(self):
        portal = api.portal.get()
        entry_pages = portal["entry-pages"]
        default_page = entry_pages[entry_pages.getDefaultPage()]
        return str(default_page.absolute_url()) + "/edit"

    def tags_selected(self):
        if 'portlet_data' in self.session.keys() and \
            'tags' in self.session['portlet_data'] and \
                len(self.session['portlet_data']['tags']) > 0:
            return True
        return False
