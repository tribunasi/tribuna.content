
"""Portlet for filterting/searching the content."""

from five import grok
from plone import api
from plone.app.portlets.portlets import base
from plone.directives import form
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFCore.interfaces import ISiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from Products.PythonScripts.standard import url_unquote

from tribuna.content import _
from tribuna.content.utils import TagsList
from tribuna.content.utils import TagsListHighlightedSidebar
from tribuna.content.config import SEARCHABLE_TYPES

# SimpleTerm(value (actual value), token (request), title (shown in browser))
# tags, sort_on, content_filters, operator


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


@form.default_value(field=ISidebarForm['tags'])
def default_tags(data):
    base_url = api.portal.get().absolute_url()
    tags = ''
    try:
        tags = data.request.URL.replace(base_url, '').strip('/').split('/')[1]
    except:
        pass

    tags = url_unquote(tags)

    if tags:
        return tags.split(',')
    return []


@form.default_value(field=ISidebarForm['all_tags'])
def default_all_tags(data):
    base_url = api.portal.get().absolute_url()
    tags = ''
    try:
        tags = data.request.URL.replace(base_url, '').strip('/').split('/')[1]
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
    return data.request.form.get("query", "")


@form.default_value(field=ISidebarForm['clicked_tag'])
def default_clicked_tag(data):
    # return data.request.form.get("clicked_tag", False)
    return False


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

    def buildGetArgs(self, home=False):
        """
        Build GET arguments from the sidebar selections.

        :returns: GET arguments to append to an URL
        :rtype:   String
        """
        if home:
            return ('?view_type=' +
                    self.request.form.get("form.widgets.view_type")[0])

        st = ""
        name = 'form.widgets.all_tags'
        if name in self.request.form:
            st += '/' + ','.join(self.request.form[name])

        name = 'form.widgets.content_filters'
        st += '&filters='
        if name in self.request.form:
            st += ','.join((i for i in self.request.form[name]
                            if i != 'all'))
        else:
            st += "None"

        for subname in ['sort_on', 'view_type']:
            name = 'form.widgets.' + subname
            if name in self.request.form:
                st += '&' + subname + '=' + ','.join(self.request.form[name])

        first_letter = st.find('&')
        if first_letter != -1:
            st = st[:first_letter] + '?' + st[first_letter + 1:]
        return st

    def buildURL(self):
        """
        If we're on home view, change to tags view, otherwise leave same.

        :returns: Base URL
        :rtype:   String
        """
        base_url = self.context.portal_url()
        get_args = ''
        url = self.request.URL.replace(base_url, '').strip('/').split('/')[0]
        if url == 'home':
            if ('form.buttons.text' in self.request.form or
                    'form.buttons.drag' in self.request.form):
                get_args = self.buildGetArgs(home=True)
            else:
                url = 'tags'
                get_args = self.buildGetArgs()
        else:
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
