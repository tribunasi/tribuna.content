"""The Article content type."""

from five import grok
from plone import api
from plone.dexterity.content import Container
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from tribuna.annotator.interfaces import ITribunaAnnotator
from zope import schema

from tribuna.content import _


class IArticle(form.Schema, ITribunaAnnotator):
    """Interface for Article content type."""

    form.primary('title')
    title = schema.TextLine(
        title=_(u"Name"),
    )

    subtitle = schema.TextLine(
        title=_(u"Article subtitle"),
        required=False,
    )

    article_author = schema.TextLine(
        title=_(u"Article author"),
        required=False,
    )

    description = schema.Text(
        title=_(u"Article description"),
        required=False,
    )

    picture = NamedBlobImage(
        title=_(u"Image"),
        description=_(u"Will be displayed on the article view."),
        required=False,
    )


class Article(Container):
    """Article model."""


class View(grok.View):
    """Article view."""
    grok.context(IArticle)
    grok.require('zope2.View')

    def update(self):
        """Redirect to @@articles view.

        XXX: this might be problematic, since sometimes we might want to
        get to the article itself.
        """
        portal = api.portal.get()
        return self.request.response.redirect(
            '{0}/@@articles/{1}'.format(
                portal.absolute_url(), self.context.id
            )
        )


class BaseView(grok.View):
    """Article view."""
    grok.context(IArticle)
    grok.require('zope2.View')
    grok.name('base-view')
