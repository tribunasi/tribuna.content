#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Viewlets."""


from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet

from tribuna.content.homepage import HomePageView
from tribuna.content.mainpage import MainPageView
from tribuna.content.portlets.sidebar import articles



class GalleryViewlet(BrowserView):
    """Viewlet that prepares and calls gallery on main page view"""

    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(GalleryViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request

    def update(self):
        pass

    def available(self, session):
        """Condition to determine if we should display the viewlet.

        If we are on the MainPageView and are viewing the gallery, return
        True.
        """

        if isinstance(self.__parent__, MainPageView):
            return True
        return False

    def render(self):
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)

        if self.available(session):
            return safe_unicode(js_template % (session['index'] + 1))
        return ""


class DefaultSessionViewlet(BrowserView):
    """Method that checks our session to get
    the article we want to show first"""

    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(DefaultSessionViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request

    def update(self):
        pass

    def set_default_content_list(self, session):
        articles(session)

    def set_default_view_type(self, session):
        session.set('view_type', 'drag')

    def checkGET(self, session):
        """Setting correct index of article that gets shown first, we get
            the article from GET request"""
        get_article = self.request.get('article')
        if get_article is not None:
            session.set('view_type', 'gallery')
            all_articles = articles(session)
            all_articles =  \
                [i.id for i in all_articles[0] + all_articles[1]]
            if get_article in all_articles:
                session.set('index', all_articles.index(get_article))
            else:
                session.set('index', 0)
        else:
            session.set('index', 0)

    def check_session(self):
        """Check if we have the data, if we don't, input defaults. Check
        for the get parameter and find the appropriate index.
        """
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        get_default = self.request.get('default')
        if get_default and "portlet_data" in session.keys():
            del session["portlet_data"]
        if get_default or 'content_list' not in session.keys():
            self.set_default_content_list(session)
        if get_default or 'view_type' not in session.keys():
            self.set_default_view_type(session)

        self.checkGET(session)

    def render(self):
        if (isinstance(self.__parent__, HomePageView)
                or isinstance(self.__parent__, MainPageView)):
            self.check_session()
        return ""

js_template = """
<script id="gallery-start">
    //$(window).load(function(){
        $('#gallery').galleryView({
            panel_width: $(window).width(),
            panel_height: $(window).height() - 30 - $('.navbar-fixed-top').height() - 16,
            //frame_width: $(window).width()/parseInt($(window).width()/220 + 1),
            frame_width: 220,
            frame_height:  54, //seems like it automatically adds 26px ...
            pause_on_hover: true,
            autoplay: false,
            filmstrip_position: "top",
            show_filmstrip_nav: true,
            enable_overlay: true,
            show_captions: true,
            transition_interval: 0,
            pointer_size: 0,
            start_frame: %d,
            slide_method: 'pointer',
            animate_pointer: false,
            transition_speed: 0,
            frame_gap: 20,
        });
    //});
</script>
"""
