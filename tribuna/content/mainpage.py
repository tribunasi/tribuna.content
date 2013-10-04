"""Views for the main page."""

from five import grok
from plone import api
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from zExceptions import NotFound

from tribuna.content.config import SEARCHABLE_TYPES
from tribuna.content.config import TYPE_TO_VIEW
from tribuna.content.utils import get_articles


class MainPageView(grok.View):
    grok.implements(IPublishTraverse)
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('articles')

    article_id = None

    def __init__(self, context, request):
        """
        Initializes the mainpage view

        :param    context: Current site context
        :type     context: Context object
        :param    request: Current HTTP request
        :type     request: Request object
        """

        self.context = context
        self.request = request

        self.getArgs = ''
        for name in self.request.form:
            self.getArgs += '&' + name + '=' + self.request.form[name]

        super(MainPageView, self).__init__(context, request)

    def publishTraverse(self, request, name):
        """
        Custom traverse method which enables us to have urls in format
        ../articles/some-article instead of
        ../articles?article=some-article.

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
        :rtype:   List
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
        if path == 'articles':
            portal = api.portal.get()
            self.request.response.redirect('{0}/home'.format(
                portal.absolute_url()))

        super(MainPageView, self).update()
        self.request.set('disable_plone.rightcolumn', 1)
        self.request.set('disable_plone.leftcolumn', 1)
        self.request.set('disable_border', 1)

    def get_close_url(self):
        """
        Return URL for close button.

        :returns: URL for close button
        :rtype:   String
        """

        unwanted = ['tags', 'comment', 'id', 'came_from']

        getArgs = ''
        tags = self.request.form.get("tags", '')

        if tags:
            for name in self.request.form:
                if name not in unwanted:
                    getArgs += '&' + name + '=' + self.request.form[name]

            if getArgs:
                getArgs = '?' + getArgs[1:]

        came_from = self.request.form.get('came_from')
        if came_from == 'home':
            view_type = self.request.form.get('view_type', '')
            if view_type:
                view_type = '?view_type=' + view_type
            url = "{0}/home{1}".format(
                self.context.portal_url(),
                view_type,
            )

            return url

        url = "{0}/tags/{1}{2}".format(
            self.context.portal_url(),
            tags,
            getArgs
        )

        return url


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
        article_type = SEARCHABLE_TYPES.get(article_type, '')
        article = catalog(id=article_id, portal_type=article_type)
        if not article:
            return ""
        article = article[0].getObject()

        # XXX: obviously view name could be 'view' for both articles and
        # comments, but there is something weid going on if I name it 'view'
        # for comments - we get some view, not the one that we have
        # defined. [jcerjak]
        view_name = TYPE_TO_VIEW.get(article.portal_type, '')
        view = api.content.get_view(
            context=article, request=self.request, name=view_name)
        return view._render_template()
