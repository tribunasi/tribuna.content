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

    def tags(self):
        """Return a catalog search result of articles that have this tag
        """

        #context = aq_inner(self.context)
        catalog = api.portal.get_tool(name='portal_catalog')
        return catalog(portal_type="tribuna.content.tag")
