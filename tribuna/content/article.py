"""The Article content type."""

from five import grok
from plone import api
from plone.dexterity.content import Container
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from tribuna.annotator.interfaces import ITribunaAnnotator
from zope import schema

from tribuna.content import _
from tribuna.annotator.utils import get_annotations


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

    def update(self):
        """Redirect to @@articles view.

        XXX: this might be problematic, since sometimes we might want to
        get to the article itself.
        """
        portal = api.portal.get()
        return self.request.response.redirect(
            '{0}/@@articles/{1}'.format(
                portal.absolute_url(), self.context.id
            )
        )

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
            self.annotation_tags = tuple(set(tup))
            return self.annotation_tags

    def _get_selected_tags(self):
        try:
            return self.selected_tags
        except AttributeError:
            # XXX: NATAN: should be this, but we need to merge with homepage-split
            # to get it to work nicely
            # selected_tags = self.request.form.get("annotation_tags")
            selected_tags = set('AnTest1,Blabla,Bleble,AnTest2,AnTest3'.split(','))
            actual_tags = ()
            self._get_annotation_tags()
            for i in selected_tags:
                if i in self.annotation_tags:
                    actual_tags += (i,)

            actual_tags = set(actual_tags)
            self.selected_tags = actual_tags

    def is_tag_selected(self):
        self._get_selected_tags()
        if self.selected_tags:
            return True
        return False

    def get_text(self):
        self._get_selected_tags()
        selected_annotations = tuple()
        for i in self.annotations:
            if len(set(i['tags']).intersection(self.selected_tags)) > 0:
                selected_annotations += (i,)

        quotes = [i['quote'] for i in selected_annotations]

        return quotes


class BaseView(grok.View):
    """Article view."""
    grok.context(IArticle)
    grok.require('zope2.View')
    grok.name('base-view')
