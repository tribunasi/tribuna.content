#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Views for the home page."""

from five import grok
from mobile.sniffer.detect import  detect_mobile_browser
from mobile.sniffer.utilities import get_user_agent
from plone import api
from plone.directives import form
from z3c.form import button
from zope import schema
from zope.interface import Interface


from tribuna.content import _
from tribuna.content.portlets.sidebar import articles


def search_articles(query, session):
    """Method for getting correct search results

    :param query: Text that we search for
    :type query: string
    :param session: Current session
    :type session: Session getObject
    """
    session['search-view']["active"] = True
    session['search-view']['query'] = query
    if "portlet_data" in session.keys():
        session["portlet_data"]["tags"] = []


class ISearchForm(form.Schema):

    search = schema.TextLine(
        title=_(u"Search"),
        required=True,
    )


class SearchForm(form.SchemaForm):
    """form handler for search form."""

    grok.name('search-form')
    grok.require('zope2.View')
    grok.permissions('zope.Public')
    grok.context(ISearchForm)

    schema = ISearchForm
    ignoreContext = True
    label = _(u"Search")
    #description = _(u"New entry page form")

    @button.buttonAndHandler(_(u'Search'))
    def handleApply(self, action):
        data, errors = self.extractData()
        query = "search" in data and data["search"] or ""
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        search_articles(query, session)
        url = api.portal.get().absolute_url()
        self.request.response.redirect("{0}/@@home-page".format(url))


class HomePageView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('home-page')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.context.session_data_manager.getSessionData(
            create=True)
        self.articles = self._get_articles()
        super(HomePageView, self).__init__(context, request)

    def check_if_default(self):
        get_default = self.request.get('default')
        if get_default:
            for i in self.session.keys():
                del self.session[i]

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
        self.check_if_default()
        articles_all = articles(self.session)
        return {
            'intersection': articles_all[0],
            'union': articles_all[1],
            'all': articles_all[0] + articles_all[1]
        }

    def only_one_tag(self):
        if 'portlet_data' in self.session.keys():
            return len(self.session['portlet_data']['tags']) == 1
        return False

    def tag_description(self):
        title = self.session['portlet_data']['tags'][0]
        with api.env.adopt_user('tags_user'):
            catalog = api.portal.get_tool(name='portal_catalog')
            tag = catalog(
                Title=title,
                portal_type='tribuna.content.tag',
            )[0].getObject()
        if not tag.description:
            return u"Description not added yet!"
        return tag.description

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
            self.is_search_view() or
            self.session["default"]):
            return False
        return True

    def show_union(self):
        if self.only_one_tag() or self.articles["union"] == []:
            return False
        return True

    def shorten_text(self, text):
        if len(text) > 140:
            return text[:140] + ' ...'
        return text

    def search_form(self):
        """Return a form which can change the entry page."""
        form1 = SearchForm(self.context, self.request)
        form1.update()
        return form1
