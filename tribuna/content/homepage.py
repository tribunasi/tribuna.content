from five import grok
from plone import api
from zope.interface import Interface

from tribuna.content import _


class HomePageView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('home-page')

    def is_text_view(self):
        """
            Get data from session, if it isn't there, send True (text is the
            basic view)
        """
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if(u'view_type' in session.keys()):
            return session[u'view_type']
        return "view"

    def articles(self):
        """ Return a catalog search result of articles that have this tag
        """

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if('content_list' in session.keys()):
            return session[u'content_list']
        return []
