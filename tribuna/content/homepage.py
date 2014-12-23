# -*- coding: utf-8 -*-
"""Views for the home page."""

from Acquisition import aq_base
from five import grok
from mobile.sniffer.detect import detect_mobile_browser
from mobile.sniffer.utilities import get_user_agent
from plone import api
from Products.Five.browser import BrowserView
from Products.PythonScripts.standard import url_quote
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse

from tribuna.content.utils import get_articles
from tribuna.content.utils import get_articles_home
from tribuna.content.utils import get_articles_search
from tribuna.content.utils import tags_published_dict


class SearchView(BrowserView):
    """View that handles the searching and then redirects to the home page
    to display the results.

    This overrides the default Plone @@search view.
    """

    def is_text_view(self):
        """
        Check if text view (base for desktop is drag, mobile only has text) is
        selected.

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

        # XXX: Temporary workaround for not getting articles twice.
        # Get the articles
        use_filters = self.request.form.get('use_filters') == 'selected'
        articles_all = get_articles_search(
            self.request.form,
            use_filters=use_filters
        )

        # Get the GET arguments
        self.getArgs = '?came_from=search'
        for name in self.request.form:
            if name == 'query':
                self.getArgs += ('&' + name + '=' +
                                 url_quote(self.request.form[name]))
            else:
                tmpArgs = self.request.form[name]
                if isinstance(tmpArgs, list):
                    tmpArgs = ','.join(tmpArgs)
                self.getArgs += '&' + name + '=' + tmpArgs

        self.articles = {
            'intersection': articles_all[0],
            'union': articles_all[1],
            'all': articles_all[0] + articles_all[1]
        }
        return self.articles

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

    def show_intersection(self):
        """
        Method for checking if we want to show the intersection

        :returns: True if we are showing intersection, False otherwise
        :rtype:   boolean
        """
        if self.articles["intersection"] == []:
            return False
        return True

    def show_union(self):
        """
        Method for checking if we want to show the union

        :returns: True if we are showing union, False otherwise
        :rtype:   boolean
        """

        if self.articles["union"] == []:
            return False
        return True


class HomePageView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('home')

    def __init__(self, context, request):
        """Initialize the homepage view.

        :param    context: Current site context
        :type     context: Context object
        :param    request: Current HTTP request
        :type     request: Request object
        """

        self.context = context
        self.request = request
        if ('form.buttons.filter' not in self.request.form and
            'form.buttons.text' not in self.request.form and
                'form.buttons.drag' not in self.request.form):
            for key in self.request.form.keys()[:]:
                if key != 'view_type':
                    del self.request.form[key]

        super(HomePageView, self).__init__(context, request)

    def is_text_view(self):
        """Check if text view (base for desktop is drag, mobile only has text)
        is selected.

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

        # XXX: Temporary workaround for not getting articles twice.
        # Get the articles
        articles_all = get_articles_home({})

        self.getArgs = '?came_from=home'
        view_type = self.request.form.get('view_type', '')
        if view_type:
            self.getArgs += '&view_type=' + view_type

        self.articles = {
            'intersection': articles_all[0],
            'union': articles_all[1],
            'all': articles_all[0] + articles_all[1]
        }
        return self.articles

    def show_intersection(self):
        """
        Method for checking if we want to show the intersection

        :returns: True if we are showing intersection, False otherwise
        :rtype:   boolean
        """
        if self.articles["intersection"] == []:
            return False
        return True

    def show_union(self):
        """
        Method for checking if we want to show the union

        :returns: True if we are showing union, False otherwise
        :rtype:   boolean
        """

        if self.articles["union"] == []:
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


class TagsView(grok.View):
    grok.implements(IPublishTraverse)
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('tags')

    def __init__(self, context, request):
        """Initialize the tags view.

        :param    context: Current site context
        :type     context: Context object
        :param    request: Current HTTP request
        :type     request: Request object
        """
        self.context = context
        self.request = request
        super(TagsView, self).__init__(context, request)

    def publishTraverse(self, request, name):
        """
        Custom traverse method which enables us to have urls in format
        ../@@tags/some-tag,other-tag instead of
        ../@@tags?tags=some-tag,other-tag.

        Works by returning the 'tags' view with "some-tag,other-tag" added to
        request.form['tags'].

        :param    request: Current request
        :type     request: Request object
        :param    name:    Name of current article/comment/image
        :type     name:    Str

        :returns: View of the current object shown in main page
        :rtype:   View object
        """
        self.request.form['tags'] = name
        return api.content.get_view(
            context=self.context,
            request=request,
            name='tags'
        )

    def is_text_view(self):
        """
        Check if text view (base for desktop is drag, mobile only has text) is
        selected.

        :returns: returns True or False, depending on text view being selected
        :rtype:   Boolean
        """
        # Get HTTP_USER_AGENT from HTTP request object
        ua = get_user_agent(self.request)
        if ua and detect_mobile_browser(ua):
            # Redirect the visitor from a web site to a mobile site
            return True

        return self.request.form.get("view_type", "drag") == "text"

    def _get_articles(self):
        """
        Get all articles for our tags view.

        :returns: Dictionary of all articles that are shown on home view
        :rtype:   Dict
        """
        articles_all = ([], [])

        # XXX: Temporary workaround for not getting articles twice.
        if('form.buttons.filter' not in self.request.form and
           'form.buttons.text' not in self.request.form and
           'form.buttons.drag' not in self.request.form):
            # Get the articles
            articles_all = get_articles(self.request.form)

            # Get the GET arguments
            self.getArgs = ''
            for name in self.request.form:
                if name == 'query':
                    self.getArgs += ('&' + name + '=' +
                                     url_quote(self.request.form[name]))
                else:
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
        Check if there is only one tag selected.

        :returns: True if one tag is selected, False otherwise
        :rtype:   Boolean
        """
        tags = self.request.form.get("tags")
        if tags:
            tags = tags.split(',')
        else:
            tags = []

        return len(tags) == 1

    def tag_text_and_image(self):
        """
        Get description and image of our tag.

        :returns: Description and image of our tag
        :rtype:   Dict
        """
        title = tags_published_dict().get(self.request.form.get("tags"))
        # If there are no published tags with this title, return defaults
        if not title:
            return {
                'text': '',
                'image': None,
            }
        with api.env.adopt_user('tags_user'):
            catalog = api.portal.get_tool(name='portal_catalog')
            tag = catalog(
                Title=title,
                portal_type='tribuna.content.tag',
            )[0].getObject()

        absolute_url = tag.absolute_url()
        tag = aq_base(tag)

        text = ""
        if tag.text:
            text = tag.text

        image = None
        if hasattr(tag, 'image') and tag.image:
            image = str(absolute_url) + "/@@images/image"

        return {
            'text': text,
            'image': image,
        }

    def show_intersection(self):
        """
        Check if we show the intersection.

        :returns: True if we are showing intersection, False otherwise
        :rtype:   Boolean
        """
        if (self.only_one_tag() or
                self.articles["intersection"] == []):
            return False
        return True

    def show_union(self):
        """
        Check if we show the union.

        :returns: True if we are showing union, False otherwise
        :rtype:   Boolean
        """
        if (self.only_one_tag() or
                self.articles["union"] == []):
            return False
        return True

    def shorten_text(self, text):
        """
        Shorten text to 140 characters

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
        Get URL of entry page edit view.

        :returns: URL of edit view
        :rtype:   str
        """
        portal = api.portal.get()
        entry_pages = portal["entry-pages"]
        default_page = entry_pages[entry_pages.getDefaultPage()]
        return str(default_page.absolute_url()) + "/edit"

    def tags_selected(self):
        """
        Check if any tags are selected.

        :returns: True if tags are selected, False otherwise
        :rtype:   Boolean
        """
        tags = self.request.form.get("tags")
        if tags:
            return True
        return False
