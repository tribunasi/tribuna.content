from five import grok
from zope import schema
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from plone import api
from plone.directives import form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage

from tribuna.content import _

from tribuna.content.article import IArticle


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

        #context = aq_inner(self.context)
        catalog = api.portal.get_tool(name='portal_catalog')
        import pdb; pdb.set_trace()
        all_articles = catalog(portal_type="tribuna.content.article")
        return [article for article in all_articles if article.getObject().tag == self.context.Title()]
