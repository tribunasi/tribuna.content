from zope.interface import implements
from zope.viewlet.interfaces import IViewlet

from Products.Five.browser import BrowserView
from Products.CMFPlone.utils import safe_unicode

from tribuna.content.homepage import HomePageView
from tribuna.content.mainpage import MainPageView
from tribuna.content.portlets.sidebar import articles
# from zope.component import getUtility
# from plone.registry.interfaces import IRegistry

# from collective.cookiecuttr.interfaces import ICookieCuttrSettings
# from plone.app.layout.analytics.view import AnalyticsViewlet


class GalleryViewlet(BrowserView):
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(GalleryViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request

    def update(self):
        pass

    def available(self, session):
        """
            If we are on the MainPageView and are viewing the gallery, return True
        """

        if isinstance(self.__parent__, MainPageView):
            return True
        return False

    def render(self):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)

        if(self.available(session)):
            return safe_unicode(js_template % (session['index'] + 1))
        return ""


class DefaultSessionViewlet(BrowserView):
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(DefaultSessionViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request

    def update(self):
        pass

    def default_content_list(self, session):
        articles(session)

    def default_view_type(self, session):
        session.set('view_type', 'text')

    def checkGET(self, session):
        get_article = self.request.get('article')
        if(get_article is not None):
            session.set('view_type', 'gallery')
            session.set('index', [
                i.tpURL() for i in session['content_list']].index(get_article))
        else:
            session.set('index', 0)

    def check_session(self):
        """
            Check if we have the data, if we don't, input defaults.
            Check for the get parameter and find the appropriate index
        """
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        if('content_list' not in session.keys()):
            self.default_content_list(session)
        if('view_type' not in session.keys()):
            self.default_view_type(session)

        self.checkGET(session)

    def render(self):
        if(isinstance(self.__parent__, HomePageView)
                or isinstance(self.__parent__, MainPageView)):
            self.check_session()
        return ""

js_template = """
<script>
    $('#gallery').galleryView({
        panel_width: $(window).width()*0.95,
        panel_height: 600,
        frame_width: $(window).width()*0.95/8,
        frame_height: 90,
        pause_on_hover: true,
        autoplay: false,
        filmstrip_position: "top",
        enable_overlay: true,
        show_captions: true,
        transition_interval: 0,
        start_frame: %d
    });
</script>
"""
