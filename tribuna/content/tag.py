from five import grok
from plone import api
from plone.app.textfield import RichText
from plone.directives import form
from plone.namedfile.field import NamedImage
from zope import schema

from tribuna.content import _


class ITag(form.Schema):
    """Interface for Tag content type
    """

    title = schema.TextLine(
        title=_(u"Name"),
    )

    description = schema.Text(
        title=_(u"A short summary"),
    )

    picture = NamedImage(
        title=_(u"Picture"),
        description=_(u"Please upload an image"),
        required=False,
    )


class View(grok.View):
    grok.context(ITag)
    grok.require('zope2.View')

    def articles(self):
        """Return a catalog search result of articles that have this tag
        """

        catalog = api.portal.get_tool(name='portal_catalog')
        all_articles = catalog(portal_type="tribuna.content.article")
        return [article for article in all_articles
                if article.review_state == 'published' and
                self.context.Title() in article.getObject().tags]
