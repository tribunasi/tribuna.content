"""The Article content type."""

from five import grok
from plone import api
from plone.dexterity.content import Container
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from Products.PythonScripts.standard import url_quote
from tribuna.annotator.interfaces import ITribunaAnnotator
from zope import schema

from tribuna.content import _
from tribuna.annotator.utils import get_annotations
from tribuna.content.utils import tags_string_to_list
from tribuna.content.utils import tags_published_dict


class IArticle(form.Schema, ITribunaAnnotator):
    """Interface for Article content type."""

    form.primary('title')
    title = schema.TextLine(
        title=_(u"Name"),
    )

    subtitle = schema.TextLine(
        title=_(u"Article subtitle"),
        required=False,
    )

    article_author = schema.TextLine(
        title=_(u"Article author"),
        required=False,
    )

    description = schema.Text(
        title=_(u"Article description"),
        required=False,
    )

    picture = NamedBlobImage(
        title=_(u"Image"),
        description=_(u"Will be displayed on the article view."),
        required=False,
    )


class Article(Container):
    """Article model."""


class View(grok.View):
    """Article view."""
    grok.context(IArticle)
    grok.require('zope2.View')

    def __init__(self, context, request):
        """
        Initializes the article view

        :param    context: Current site context
        :type     context: Context object
        :param    request: Current HTTP request
        :type     request: Request object
        """

        self.context = context
        self.request = request

        self.getArgs = ''
        for name in self.request.form:
            if name not in ["annotation_tags", 'type', 'id']:
                if name == 'query':
                    self.getArgs += ('&' + name + '=' +
                                     url_quote(self.request.form[name]))
                else:
                    self.getArgs += '&' + name + '=' + self.request.form[name]

        if self.getArgs:
                self.getArgs = '?' + self.getArgs[1:]

        super(View, self).__init__(context, request)

    def update(self):
        """Redirect to articles view.

        XXX: this might be problematic, since sometimes we might want to
        get to the article itself.
        """
        portal = api.portal.get()
        return self.request.response.redirect(
            '{0}/articles/{1}'.format(
                portal.absolute_url(), self.context.id
            )
        )

    def get_selected_tags(self):
        return tags_string_to_list(self.request.form.get('tags'))

    def _setup_annotations(self):
        # if self.annotations:
        #     return self.annotations
        # path = '/'.join(self.context.getPhysicalPath())
        # return get_annotations(path)
        try:
            self.annotations
        except AttributeError:
            path = '/'.join(self.context.getPhysicalPath())
            self.annotations = get_annotations(path)

    def _get_annotation_tags(self):
        try:
            return self.annotation_tags
        except AttributeError:
            self._setup_annotations()
            tags_generator = (annot['tags'] for annot in self.annotations)
            tup = tuple()
            for i in tags_generator:
                tup += i
            self.annotation_tags = tuple(sorted(set(tup), key=str.lower))
            return self.annotation_tags

    def _get_selected_annotation_tags(self):
        try:
            return self.selected_annotation_tags
        except AttributeError:
            selected_annotation_tags = self.request.form.get("annotation_tags")

            if not selected_annotation_tags:
                self.selected_annotation_tags = []
                return self.selected_annotation_tags

            selected_annotation_tags = selected_annotation_tags.split(',')
            tags_dict = tags_published_dict()
            selected_annotation_tags = tuple((tags_dict.get(i) for
                                              i in selected_annotation_tags))

            actual_tags = ()
            self._get_annotation_tags()
            for i in selected_annotation_tags:
                if i in self.annotation_tags:
                    actual_tags += (i,)

            actual_tags = set(actual_tags)
            self.selected_annotation_tags = actual_tags
            return self.selected_annotation_tags

    def is_tag_selected(self):
        self._get_selected_annotation_tags()
        if self.selected_annotation_tags:
            return True
        return False

    def get_text(self):
        self._get_selected_annotation_tags()
        selected_annotations = tuple()
        for i in self.annotations:
            if(len(set(i['tags']).intersection(self.selected_annotation_tags))
               > 0):
                selected_annotations += (i,)

        quotes = [i['quote'] for i in selected_annotations]

        return quotes

    def get_annotation_tag_url(self, tag_title):
        catalog = api.portal.get_tool(name='portal_catalog')
        tag_id = catalog(
            Title=tag_title,
            portal_type='tribuna.content.tag'
        )[0].id
        args = self.getArgs
        args_exist = False
        if args:
            args_exist = True

        url_annotation_tags = self.request.form.get("annotation_tags", '')
        if url_annotation_tags:
            url_annotation_tags = url_annotation_tags.split(',')
            if tag_id in url_annotation_tags:
                url_annotation_tags.remove(tag_id)
            else:
                url_annotation_tags.append(tag_id)
        else:
            url_annotation_tags = [tag_id]

        # If we didn't just delete the last one
        if url_annotation_tags:
            args += '&annotation_tags=' + ','.join(url_annotation_tags)

        args += "&id=" + self.context.id
        args += "&type=article"

        if not args_exist:
            first_letter = args.find('&')
            if first_letter != -1:
                args = args[:first_letter] + '?' + args[first_letter + 1:]

        return api.portal.get().absolute_url() + '/get-article' + args

    def is_annotation_tag_selected(self, tag_title):
        try:
            return tag_title in self.selected_annotation_tags
        except AttributeError:
            return tag_title in self._get_selected_annotation_tags()


class BaseView(grok.View):
    """Article view."""
    grok.context(IArticle)
    grok.require('zope2.View')
    grok.name('base-view')
