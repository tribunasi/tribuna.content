from five import grok
from plone import api
from zope.interface import Interface

from tribuna.content import _


class HomePageView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('home-page')

    # Should get tag from request
    #tag = "Tag 1"

    # number of articles to be shown
    limit = 6

    def is_text_view(self):
        if "textview" in self.request.form:
            if self.request.form["textview"] == "True":
                return True

    def articles(self):
        """ Return a catalog search result of articles that have this tag
        """
        #import pdb; pdb.set_trace()
        catalog = api.portal.get_tool(name='portal_catalog')
        all_articles = catalog(portal_type="tribuna.content.article", locked_on_home=True, review_state="published", sort_on="Date", sort_limit=self.limit)[:self.limit]
        currentLen = len(all_articles)
        #import pdb; pdb.set_trace()
        if currentLen < self.limit:
            all_articles += catalog(portal_type="tribuna.content.article", locked_on_home=False, review_state="published", sort_on="Date", sort_limit=self.limit-currentLen)[:self.limit-currentLen]

        if not all_articles:
            return []
        return [article.getObject() for article in all_articles]
