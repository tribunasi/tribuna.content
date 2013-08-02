#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Views for the home page."""

from five import grok
from plone import api
from plone.directives import form
from z3c.form import button
from zope import schema
from zope.interface import Interface

from tribuna.content import _
from tribuna.content.portlets.sidebar import articles as sidebar_articles


def search_articles(query, session):
    """Method for getting correct search results

    :param query: Text that we search for
    :type query: string
    :param session: Current session
    :type session: Session getObject
    """
    #session['content_list']['union'] = []
    session['search-view']["active"] = True
    session['search-view']['query'] = query
    if "portlet_data" in session.keys():
        session["portlet_data"]["tags"] = []


class ISearchForm(form.Schema):

    search = schema.TextLine(
        title=_(u"Search"),
        required=True
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
        #if errors:
        #    self.status = self.formErrorsMessage
        #    return
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

    def check_if_default(self):
        get_default = self.request.get('default')
        if get_default:
            sdm = self.context.session_data_manager
            session = sdm.getSessionData(create=True)
            for i in session.keys():
                del session[i]

    def is_text_view(self):
        """Check if text view (this is the basic view) is selected.

        Read data from the session, if it isn't there, return True.
        """
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if 'view_type' in session.keys():
            if session['view_type'] == 'drag':
                return False
        return True

    def articles(self, operator):
        """Return a catalog search result of articles that have the selected
        tag.

        :param operator: Operator used for articles filtering, has to be from:
                        ("union", "intersection", "all")
        :type operator: string
        """

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        articles_all = sidebar_articles(session)
        if operator == "intersection":
            return articles_all[0]
        if operator == "union":
            return articles_all[1]
        else:
            return articles_all[0] + articles_all[1]

    def only_one_tag(self):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if 'portlet_data' in session.keys() :
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

    def tag_picture(self):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)

        title = session['portlet_data']['tags'][0]
        with api.env.adopt_user('tags_user'):
            catalog = api.portal.get_tool(name='portal_catalog')
            tag = catalog(
                Title=title,
                portal_type='tribuna.content.tag',
            )[0].getObject()
        if not hasattr(tag, 'image') or not tag.image:
            return None
        return str(tag.absolute_url()) + "/@@images/image"

    def show_intersection(self):
        if self.only_one_tag() is True:
            return False
        if self.articles("intersection") == []:
            return False
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if "search-view" in session.keys() and session["search-view"]:
            return False
        return True

    def show_union(self):
        if self.only_one_tag() is True:
            return False
        if self.articles("union") == []:
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

    def is_search_view(self):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if "search-view" in session.keys() and session["search-view"]:
            return True
        return False
