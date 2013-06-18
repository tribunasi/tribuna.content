from five import grok
from plone import api
from zope.interface import Interface

from tribuna.content import _


class MainPageView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('main-page')

    def articles(self):
        """ Return a catalog search result of articles that have this tag
        """

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if('content_list' in session.keys()):
            return session[u'content_list']
        return []
