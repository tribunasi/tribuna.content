from five import grok
from plone import api
from zope.interface import Interface

from tribuna.content import _


class HomePageView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('home-page')

    # Should get tag from request
    tag = "Tag 1"

    # number of articles to be shown
    limit = 2

    # def __call__(self):
    #     super(grok.View).__call__(self)

    def changeTag(self,):
        """ Changes the tag which articles should be shown for
        """

    def articles(self):
        """ Return a catalog search result of articles that have this tag
        """

        catalog = api.portal.get_tool(name='portal_catalog')
        all_articles = catalog(portal_type="tribuna.content.article", review_state="published", sort_on="Date")
        if not all_articles:
            return []
        return [article for article in all_articles
                if self.tag in article.getObject().tags][:self.limit]
