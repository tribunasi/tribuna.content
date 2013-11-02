"""Portlet for filterting/searching the content."""

from five import grok
from plone import api
from plone.app.portlets.portlets import base
from plone.directives import form
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFCore.interfaces import ISiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PythonScripts.standard import url_quote
from Products.PythonScripts.standard import url_unquote
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from tribuna.content import _
from tribuna.content.utils import TagsList
from tribuna.content.utils import TagsListHighlightedSidebar
from tribuna.content.config import SEARCHABLE_TYPES


class ISidebarForm(form.Schema):
    """ Defining form fields for sidebar portlet """

    form.widget(tags=CheckBoxFieldWidget)
    tags = schema.List(
        title=_(u"Tags"),
        value_type=schema.Choice(source=TagsListHighlightedSidebar()),
        required=False,
        default=[],
    )

    form.widget(all_tags=CheckBoxFieldWidget)
    all_tags = schema.List(
        title=_(u"All tags"),
        value_type=schema.Choice(source=TagsList()),
        required=False,
        default=[],
    )

    sort_on = schema.Choice(
        title=_(u"Type of sorting"),
        vocabulary=SimpleVocabulary([
            SimpleTerm('latest', 'latest', _(u'Latest')),
            SimpleTerm('comments', 'comments', _(u'Nr. of comments')),
        ]),
    )

    view_type = schema.Choice(
        title=_(u"View type"),
        vocabulary=SimpleVocabulary([
            SimpleTerm('drag', 'drag', _(u'Drag')),
            SimpleTerm('text', 'text', _(u'Text')),
        ]),
    )

    form.widget(content_filters=CheckBoxFieldWidget)
    content_filters = schema.List(
        title=_(u"Content filters"),
        value_type=schema.Choice(source=SimpleVocabulary([
            SimpleTerm('all', 'all', _(u'All')),
            SimpleTerm('article', 'article', _(u'Article')),
            SimpleTerm('comment', 'comment', _(u'Comment')),
            SimpleTerm('image', 'image', _(u'Image')),
            SimpleTerm('annotation', 'annotation', _(u'Annotation')),
        ])),
        required=False,
    )

    query = schema.TextLine(title=_(u"Query"), default=u"", required=False)
    clicked_tag = schema.Bool(default=False)
    use_filters = schema.Bool(default=True)


@form.default_value(field=ISidebarForm['tags'])
def default_tags(data):
    query = data.request.form.get('query')
    if query:
        tags = url_unquote(data.request.form.get('tags'))
    else:
        base_url = api.portal.get().absolute_url()
        tags = ''
        try:
            tags = data.request.URL.replace(base_url, '').strip('/').split('/'
                                                                           )[1]
        except:
            pass

        tags = url_unquote(tags)

    if tags:
        return tags.split(',')
    return []


@form.default_value(field=ISidebarForm['all_tags'])
def default_all_tags(data):
    query = data.request.form.get('query')
    if query:
        tags = url_unquote(data.request.form.get('tags'))
    else:
        base_url = api.portal.get().absolute_url()
        tags = ''
        try:
            tags = data.request.URL.replace(base_url, '').strip('/').split('/'
                                                                           )[1]
        except:
            pass

        tags = url_unquote(tags)

    if tags:
        return tags.split(',')
    return []


@form.default_value(field=ISidebarForm['sort_on'])
def default_sort_on(data):
    return data.request.form.get("sort_on", "latest")


@form.default_value(field=ISidebarForm['view_type'])
def default_view_type(data):
    return data.request.form.get("view_type", "drag")


@form.default_value(field=ISidebarForm['content_filters'])
def default_content_filters(data):
    filters = data.request.form.get("filters")
    if not filters:
        return ['all'] + SEARCHABLE_TYPES.keys()
    filters = filters.split(',')
    if set(filters) == set(SEARCHABLE_TYPES.keys()):
        return ['all'] + filters
    return filters


@form.default_value(field=ISidebarForm['query'])
def default_query(data):
    return data.request.form.get("query", "").strip('"')


@form.default_value(field=ISidebarForm['clicked_tag'])
def default_clicked_tag(data):
    return False


@form.default_value(field=ISidebarForm['use_filters'])
def default_use_filters(data):
    return data.request.form.get('use_filters') == 'selected'


class SidebarForm(form.SchemaForm):
    """ Defining form handler for sidebar portlet
    """
    grok.name('my-form')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    schema = ISidebarForm
    ignoreContext = True

    label = _(u"Select appropriate tags")
    description = _(u"Tags selection form")

    def buildGetArgs(self, home=False, search=False):
        """
        Build GET arguments from the sidebar selections.

        :returns: GET arguments to append to an URL
        :rtype:   String
        """
        other_names = ['sort_on', 'view_type']

        if home:
            return ('?view_type=' +
                    self.request.form.get("form.widgets.view_type")[0])

        # Append tags, depending on if we're searching or not
        st = ""
        name = 'form.widgets.all_tags'
        if not search:
            if name in self.request.form:
                st += '/' + ','.join(self.request.form[name])
        else:
            if name in self.request.form:
                st += '&tags=' + ','.join(self.request.form[name])
            st += '&query="{0}"'.format(
                url_quote(self.request.form.get('form.widgets.query'))
            )
            other_names.append('use_filters')

        # Append all filters except none
        name = 'form.widgets.content_filters'
        st += '&filters='
        if name in self.request.form:
            st += ','.join((i for i in self.request.form[name]
                            if i != 'all'))
        # If we have no filters, make sure we save that too
        else:
            st += "None"

        # Append sort_on and view_type
        for subname in other_names:
            name = 'form.widgets.' + subname
            if name in self.request.form:
                st += '&' + subname + '=' + ','.join(self.request.form[name])

        # Change the first GET parameter from &name=value to ?name=value
        first_letter = st.find('&')
        if first_letter != -1:
            st = st[:first_letter] + '?' + st[first_letter + 1:]
        return st

    def buildURL(self):
        """
        If we're on home view, change to tags view.
        If we have a query, change to search view.
        Otherwise leave same.

        :returns: Base URL
        :rtype:   String
        """
        base_url = self.context.portal_url()
        get_args = ''
        url = self.request.URL.replace(base_url, '').strip('/').split('/')[0]
        query = url_quote(self.request.form.get('form.widgets.query'))
        clicked_tag = self.request.form.get('form.widgets.clicked_tag')

        # If we have a query, search on it ...
        if query:
            # ... unless we clicked a tag, then we want to go back to tags view
            if clicked_tag:
                url = 'tags'
                get_args = self.buildGetArgs()
            else:
                url = 'search'
                get_args = self.buildGetArgs(search=True)
        # If we do not have a query, either stay at home or go to tags
        else:
            if url == 'home':
                # If we're at home view and only clicked text/drag view, stay
                # on home, otherwise go to tags
                if ('form.buttons.text' in self.request.form or
                        'form.buttons.drag' in self.request.form):
                    get_args = self.buildGetArgs(home=True)
                else:
                    url = 'tags'
                    get_args = self.buildGetArgs()
            # If we do not have a query and aren't on home, go to tags
            else:
                url = 'tags'
                get_args = self.buildGetArgs()
        url = base_url + '/' + url

        return url + get_args

    @button.buttonAndHandler(_(u'Filter'))
    def handleFilter(self, action):
        """
        Builds an URL with GET arguments gotten from self.request.form and
        redirects there.

        :param    action: action selected on form
        :type     action: str
        """

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        url = self.buildURL()
        self.request.response.redirect(url)

    @button.buttonAndHandler(_(u'Text'))
    def handleText(self, action):
        """
        Builds an URL with GET arguments gotten from self.request.form and
        redirects there. Also changes view_type to 'text' (in JS).

        :param    action: action selected on form
        :type     action: str
        """

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        url = self.buildURL()
        self.request.response.redirect(url)

    @button.buttonAndHandler(_(u'Drag'))
    def handleDrag(self, action):
        """
        Builds an URL with GET arguments gotten from self.request.form and
        redirects there. Also changes view_type to 'drag' (in JS).

        :param    action: action selected on form
        :type     action: str
        """

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        url = self.buildURL()
        self.request.response.redirect(url)


class ISidebarPortlet(IPortletDataProvider):
    pass


class Assignment(base.Assignment):
    implements(ISidebarPortlet)

    heading = _(u"Sidebar navigation")
    description = _(u"Use this portlet for tag navigation.")

    title = _(u"Sidebar portlet")


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('sidebar.pt')

    def portlet_data(self):
        """
        Method for getting sidebar form for rendering

        :returns: our sidebar form
        :rtype:   Form object
        """
        form1 = SidebarForm(self.context, self.request)
        form1.update()
        return form1


class AddForm(base.NullAddForm):
    def create(self):
        return Assignment()
