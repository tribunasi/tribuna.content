from five import grok
from plone import api
from zope.interface import Interface

from tribuna.content import _

#grok.templatedir('mainpage_templates')


class MainPageView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('main-page')

    #grok.template('mainpage.pt')

    def articles(self):
        """ Return a catalog search result of articles that have this tag
        """

        catalog = api.portal.get_tool(name='portal_catalog')

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        tags = session["tags"]["tags"]
        if session["is_union"] is True:
            x = catalog(portal_type="tribuna.content.article", review_state="published", sort_on="Date", Subject={"query": tags, "operator": "or"})
            return x
        else:
            return catalog(portal_type="tribuna.content.article", review_state="published", sort_on="Date", Subject={"query": tags, "operator": "and"})
