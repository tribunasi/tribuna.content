from five import grok
from plone import api
from zope.interface import Interface

from tribuna.content import _
from tribuna.content.portlets.sidebar import articles


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
        if('view_type' in session.keys()):
            return session['view_type']
        return "view"

    def articles(self):
        """ Return a catalog search result of articles that have this tag
        """

        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if('content_list' in session.keys()):
            return session['content_list']
        return []

    def checkGET(self):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)

        # defaults
        if('content_list' not in session.keys()):
            articles(session)
        if('view_type' not in session.keys()):
            session.set('view_type', 'text')
        session.set('index', 0)

        get_article = self.request.get('article')
        if(get_article is not None):
            session.set('view_type', 'gallery')
            session.set('index', [i.tpURL() for i in session['content_list']].index(get_article))
