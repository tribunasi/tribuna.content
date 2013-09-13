#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Views for the main page."""

from five import grok
from plone import api
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from zExceptions import NotFound

from tribuna.content.utils import get_articles


class MainPageView(grok.View):
    grok.implements(IPublishTraverse)
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('articles')

    article_id = None

    def publishTraverse(self, request, name):
        """
        Custom traverse method which enables us to have urls in format
        ../@@articles/some-article instead of
        ../@@articles?article=some-article.

        :param    request: Current request
        :type     request: Request object
        :param    name:    Name of current article/comment/image
        :type     name:    str

        :returns: View of the current object shown in main page
        :rtype:   View object
        """
        # Need this hack so resolving url for an uuid works (e.g. article
        # images use this view to get the real url)
        if name == 'resolveuid':
            return api.content.get_view(
                context=self.context,
                request=request,
                name=name
            )
        if self.article_id is None:
            self.article_id = name
            return self
        else:
            raise NotFound()

    def articles_all(self):
        """
        Return all articles that match the criteria.

        :returns: All articles that match
        :rtype:   list
        """
        if not self.article_id:
            return []
        articles = get_articles(self.request.form)
        all_articles = articles[0] + articles[1]

        if self.article_id in [i.id for i in all_articles]:
            return all_articles
        else:
            catalog = api.portal.get_tool(name='portal_catalog')
            article = catalog(id=self.article_id)
            return article and [article[0].getObject()] or []

    def update(self):
        """Disabling plone columns that we don't want here."""

        # redirect to homepage if no article id was provided
        path = self.request.getURL().strip('/').split('/')[-1]
        if path == '@@articles':
            portal = api.portal.get()
            self.request.response.redirect('{0}/home'.format(
                portal.absolute_url()))

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
        """
        Method for rendering our view

        :returns: Rendered HTML for our view
        :rtype:   HTML
        """
        article_id = self.request.get('id')
        article_type = self.request.get('type')
        if not article_id:
            return ""
        catalog = api.portal.get_tool(name='portal_catalog')
        if article_type == "comment":
            article_type = "Discussion Item"
        elif article_type == "article":
            article_type = "tribuna.content.article"
        else:
            article_type = "tribuna.content.image"
        article = catalog(id=article_id, portal_type=article_type)
        if not article:
            return ""
        article = article[0].getObject()

        # XXX: obviously view name could be 'view' for both articles and
        # comments, but there is something weid going on if I name it 'view'
        # for comments - we get some view, not the one that we have
        # defined. [jcerjak]
        view_name = (
            article.portal_type == 'Discussion Item' and 'comment-view' or
            (article.portal_type == 'tribuna.content.image' and 'image-view') or 'view'
        )
        view = api.content.get_view(
            context=article, request=self.request, name=view_name)
        return view._render_template()
