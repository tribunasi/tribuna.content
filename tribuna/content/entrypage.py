
from five import grok
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from tribuna.content import _
from zope import schema


class IEntryPage(form.Schema):
    """Interface for EntryPage content type
    """

    title = schema.TextLine(
        title=_(u"Name"),
    )

    picture = NamedBlobImage(
        title=_(u"Please upload an image"),
        required=False,
    )


class View(grok.View):
    grok.context(IEntryPage)
    grok.require('zope2.View')

    # def articles(self):
    #     """Return a catalog search result of articles that have this tag
    #     """
    #     #import pdb; pdb.set_trace()
    #     catalog = api.portal.get_tool(name='portal_catalog')
    #     all_articles = catalog(portal_type="tribuna.content.article")
    #     return [article for article in all_articles
    #             if article.review_state == 'published']
