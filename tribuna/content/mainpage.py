#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Views for the main page."""

from five import grok
from plone import api
from zope.interface import Interface

from tribuna.content.portlets.sidebar import articles as get_articles


class MainPageView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('main-page')

    def articles_all(self):
        """Return all articles that match the criteria."""
        article_id = self.request.get('article')
        if not article_id:
            return []
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        articles = get_articles(session)
        all_articles = articles[0] + articles[1]
        if article_id in [i.id for i in all_articles]:
            return all_articles
        else:
            catalog = api.portal.get_tool(name='portal_catalog')
            article = catalog(id=article_id)
            return article and [article[0].getObject()] or []

    def update(self):
        """Disabling plone columns that we don't want here."""
        super(MainPageView, self).update()
        self.request.set('disable_plone.rightcolumn', 1)
        self.request.set('disable_plone.leftcolumn', 1)
        self.request.set('disable_border', 1)


class GetArticle(grok.View):
    """View for getting and rendering an article for the provided id
    (loaded with AJAX from mainpage).
    """
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('get-article')

    def render(self):
        article_id = self.request.get('id')
        if not article_id:
            return ""
        catalog = api.portal.get_tool(name='portal_catalog')
        article = catalog(id=article_id)
        if not article:
            return ""
        article = article[0].getObject()

        # XXX: obviously view name could be 'view' for both articles and
        # comments, but there is something weid going on if I name it 'view'
        # for comments - we get some view, not the one that we have
        # defined. [jcerjak]
        view_name = (
            article.portal_type == 'Discussion Item' and 'comment-view' or
            'view'
        )
        view = api.content.get_view(
            context=article, request=self.request, name=view_name)
        return view._render_template()
