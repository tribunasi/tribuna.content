# -*- coding: utf-8 -*-

"""Views for the home page."""

from five import grok
from mobile.sniffer.detect import detect_mobile_browser
from mobile.sniffer.utilities import get_user_agent
from plone import api
from plone.app.search.browser import quote_chars
from Products.Five.browser import BrowserView
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from zExceptions import NotFound

from tribuna.content import _
from tribuna.content.utils import get_articles
from tribuna.content.utils import reset_session
from tribuna.content.utils import tags_published_dict


def search_articles(query, session):
    """Method for getting correct search results

    :param query: Text that we search for
    :type  query: string
    :param session: Current session
    :type  session: Session getObject
    """
    if 'search-view' not in session.keys():
        return
    session['search-view']["active"] = True
    session['search-view']['query'] = query
    if "portlet_data" in session.keys():
        session["portlet_data"]["tags"] = []


class SearchView(BrowserView):
    """View that handles the searching and then redirects to the home page
    to display the results.

    This overrides the default Plone @@search view.
    """

    def __call__(self):
        """
        Makes the search and redirects to correct URL
        """
        query = quote_chars(self.request.form.get('SearchableText', ''))
        if query:
            query = query + '*'
        sdm = self.context.session_data_manager
        session = sdm.getSessionData(create=True)
        search_articles(query, session)
        url = api.portal.get().absolute_url()
        self.request.response.redirect("{0}/home".format(url))


class HomePageView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('home')

    def __init__(self, context, request):
        """
        Initializes the homepage view

        :param    context: Current site context
        :type     context: Context object
        :param    request: Current HTTP request
        :type     request: Request object
        """

        self.context = context
        self.request = request
        self.session = self.context.session_data_manager.getSessionData(
            create=True)
        self.articles = self._get_articles()
        super(HomePageView, self).__init__(context, request)

    def set_default_view_type(self, session):
        """
        Set session to default view type

        :param    session: current session
        :type     session: Session object
        """

        session.set('view_type', 'drag')

    def set_default_filters(self, session):
        """
        Set default filters on session

        :param    session: Current session
        :type     session: Session object
        """

        session.set('portlet_data', {
            'all_tags': [],
            'tags': [],
            'sort_on': 'latest',
            'content_filters': ['article', 'comment', 'image']
        })

    def check_if_default(self):
        """
        Checks if session is set to default
        """

        get_default = self.request.get('default')
        reset_session(self.session, get_default)

    def is_text_view(self):
        """
        Check if text view (this is the basic view) is selected.

        :returns: returns True or False, depending on text view being selected
        :rtype:   boolean
        """
        # Get HTTP_USER_AGENT from HTTP request object
        ua = get_user_agent(self.request)
        if ua and detect_mobile_browser(ua):
            # Redirect the visitor from a web site to a mobile site
            True
        elif 'view_type' in self.session.keys():
            if self.session['view_type'] == 'drag':
                return False
        return True

    def _get_articles(self):
        """
        Get all articles for our home view

        :returns: Dictionary of all articles that are shown on home view
        :rtype:   dict
        """
        # XXX: The viewlet takes care of that, we should either move everything
        # here or leave everything there
        self.check_if_default()
        articles_all = get_articles(self.session)
        return {
            'intersection': articles_all[0],
            'union': articles_all[1],
            'all': articles_all[0] + articles_all[1]
        }

    def only_one_tag(self):
        """
        Method to see if there is only one tag selected

        :returns: True if one tag is selected, false otherwise
        :rtype:   boolean
        """
        if 'portlet_data' in self.session.keys():
            return len(self.session['portlet_data']['tags']) == 1
        return False

    def tag_text(self):
        """
        Method for getting description of our tag

        :returns: Description of our tag
        :rtype:   string
        """
        title = self.session['portlet_data']['tags'][0]
        with api.env.adopt_user('tags_user'):
            catalog = api.portal.get_tool(name='portal_catalog')
            tag = catalog(
                Title=title,
                portal_type='tribuna.content.tag',
            )[0].getObject()
        if not tag.text:
            return _(u"Description not added yet!")
        return tag.text

    def tag_picture(self):
        """
        Method for getting picture of our tag

        :returns: Url of picture of our tag
        :rtype:   str
        """
        title = self.session['portlet_data']['tags'][0]
        with api.env.adopt_user('tags_user'):
            catalog = api.portal.get_tool(name='portal_catalog')
            tag = catalog(
                Title=title,
                portal_type='tribuna.content.tag',
            )[0].getObject()
        if not hasattr(tag, 'image') or not tag.image:
            return None
        return str(tag.absolute_url()) + "/@@images/image"

    def is_search_view(self):
        """
        Method that checks if we are in search view

        :returns: True if we are in search view, False otherwise
        :rtype:   boolean
        """
        if ("search-view" in self.session.keys() and
                self.session["search-view"]["active"]):
            return True
        return False

    def show_intersection(self):
        """
        Method for checking if we want to show the intersection

        :returns: True if we are showing intersection, False otherwise
        :rtype:   boolean
        """
        if (self.only_one_tag() or
            self.articles["intersection"] == [] or
                self.is_search_view()):
            return False
        return True

    def show_union(self):
        """
        Method for checking if we want to show the union

        :returns: True if we are showing union, False otherwise
        :rtype:   boolean
        """
        if (self.only_one_tag() or
            self.articles["union"] == [] or
                self.is_search_view()):
            return False
        return True

    def shorten_text(self, text):
        """
        Method for shortening text to 140 characters

        :param    text: Text that we are shortening
        :type     text: str

        :returns: Shortened text
        :rtype:   str
        """
        if len(text) > 140:
            return text[:140] + ' ...'
        return text

    def entry_page_edit(self):
        """
        Method for getting url of edit view of entry page

        :returns: URL of edit view
        :rtype:   str
        """
        portal = api.portal.get()
        entry_pages = portal["entry-pages"]
        default_page = entry_pages[entry_pages.getDefaultPage()]
        return str(default_page.absolute_url()) + "/edit"

    def tags_selected(self):
        """
        Method for checking if any tags are selected

        :returns: True if tags are selected, False otherwise
        :rtype:   boolean
        """
        if 'portlet_data' in self.session.keys() and \
            'tags' in self.session['portlet_data'] and \
                len(self.session['portlet_data']['tags']) > 0:
            return True
        return False


class TagsView(grok.View):
    grok.implements(IPublishTraverse)
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('tags')

    def __init__(self, context, request):
        """
        Initializes the homepage view

        :param    context: Current site context
        :type     context: Context object
        :param    request: Current HTTP request
        :type     request: Request object
        """

        self.context = context
        self.request = request
        self.session = self.context.session_data_manager.getSessionData(
            create=True)
        super(TagsView, self).__init__(context, request)

    def publishTraverse(self, request, name):
        """
        Custom traverse method which enables us to have urls in format
        ../@@tags/some-article instead of
        ../@@tags?article=some-article.

        :param    request: Current request
        :type     request: Request object
        :param    name:    Name of current article/comment/image
        :type     name:    str

        :returns: View of the current object shown in main page
        :rtype:   View object
        """
        # Need this hack so resolving url for an uuid works (e.g. article
        # images use this view to get the real url)
        self.request.form['tags'] = name
        return api.content.get_view(
            context=self.context,
            request=request,
            name='tags'
        )

    def is_text_view(self):
        """
        Check if text view (this is the basic view) is selected.

        :returns: returns True or False, depending on text view being selected
        :rtype:   boolean
        """
        # Get HTTP_USER_AGENT from HTTP request object
        ua = get_user_agent(self.request)
        if ua and detect_mobile_browser(ua):
            # Redirect the visitor from a web site to a mobile site
            return True

        return self.request.form.get("view_type", "drag") == "text"

    def _get_articles(self):
        """
        Get all articles for our tags view

        :returns: Dictionary of all articles that are shown on home view
        :rtype:   dict
        """
        articles_all = ([], [])
        if('form.buttons.filter' not in self.request.form and
           'form.buttons.text' not in self.request.form and
           'form.buttons.drag' not in self.request.form):
            # Get the articles
            articles_all = get_articles(self.request.form)

            # Get the GET arguments
            self.getArgs = ''
            for name in self.request.form:
                self.getArgs += '&' + name + '=' + self.request.form[name]

            if self.getArgs:
                self.getArgs = '?' + self.getArgs[1:]

        self.articles = {
            'intersection': articles_all[0],
            'union': articles_all[1],
            'all': articles_all[0] + articles_all[1]
        }
        return self.articles

    def only_one_tag(self):
        """
        Method to see if there is only one tag selected

        :returns: True if one tag is selected, false otherwise
        :rtype:   boolean
        """
        import pdb; pdb.set_trace()
        tags = self.request.form.get("tags")
        if tags:
            tags = tags.split(',')
        else:
            tags = []

        return len(tags) == 1

    def tag_text_and_image(self):
        """
        Method for getting description of our tag

        :returns: Description of our tag
        :rtype:   string
        """
        import pdb; pdb.set_trace()
        title = tags_published_dict().get(self.request.form.get("tags"))
        with api.env.adopt_user('tags_user'):
            catalog = api.portal.get_tool(name='portal_catalog')
            tag = catalog(
                Title=title,
                portal_type='tribuna.content.tag',
            )[0].getObject()

        text = ""
        if not tag.text:
            text = _(u"Description not added yet!")
        else:
            text = tag.text

        image = None
        if not hasattr(tag, 'image') or not tag.image:
            image = None
        else:
            image = str(tag.absolute_url()) + "/@@images/image"

        return {
            'text': text,
            'image': image,
        }


    def tag_picture(self):
        """
        Method for getting picture of our tag

        :returns: Url of picture of our tag
        :rtype:   str
        """
        title = self.session['portlet_data']['tags'][0]
        with api.env.adopt_user('tags_user'):
            catalog = api.portal.get_tool(name='portal_catalog')
            tag = catalog(
                Title=title,
                portal_type='tribuna.content.tag',
            )[0].getObject()
        if not hasattr(tag, 'image') or not tag.image:
            return None
        return str(tag.absolute_url()) + "/@@images/image"

    def is_search_view(self):
        """
        Method that checks if we are in search view

        :returns: True if we are in search view, False otherwise
        :rtype:   boolean
        """
        if ("search-view" in self.session.keys() and
                self.session["search-view"]["active"]):
            return True
        return False

    def show_intersection(self):
        """
        Method for checking if we want to show the intersection

        :returns: True if we are showing intersection, False otherwise
        :rtype:   boolean
        """

        # XXX: V tagsview.pt se pojavlja znotraj repeata. Fix!
        if (self.only_one_tag() or
            self.articles["intersection"] == [] or
                self.is_search_view()):
            return False
        return True

    def show_union(self):
        """
        Method for checking if we want to show the union

        :returns: True if we are showing union, False otherwise
        :rtype:   boolean
        """

        # XXX: Verjetno isto kot zgoraj!
        if (self.only_one_tag() or
            self.articles["union"] == [] or
                self.is_search_view()):
            return False
        return True

    def shorten_text(self, text):
        """
        Method for shortening text to 140 characters

        :param    text: Text that we are shortening
        :type     text: str

        :returns: Shortened text
        :rtype:   str
        """
        if len(text) > 140:
            return text[:140] + ' ...'
        return text

    def entry_page_edit(self):
        """
        Method for getting url of edit view of entry page

        :returns: URL of edit view
        :rtype:   str
        """
        portal = api.portal.get()
        entry_pages = portal["entry-pages"]
        default_page = entry_pages[entry_pages.getDefaultPage()]
        return str(default_page.absolute_url()) + "/edit"

    def tags_selected(self):
        """
        Method for checking if any tags are selected

        :returns: True if tags are selected, False otherwise
        :rtype:   boolean
        """
        if 'portlet_data' in self.session.keys() and \
            'tags' in self.session['portlet_data'] and \
                len(self.session['portlet_data']['tags']) > 0:
            return True
        return False
