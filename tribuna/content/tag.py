from five import grok
from plone import api
from plone.directives import form
from plone.namedfile.field import NamedImage
from zope import schema
from zope.container.interfaces import IObjectAddedEvent
from zope.container.interfaces import IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

from tribuna.content import _


class TagsList(object):
    grok.implements(IContextSourceBinder)

    def __init__(self):
        pass

    def __call__(self, context):
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog({
            'portal_type': 'tribuna.content.tag',
            'review_state': 'published',
        })

        terms = []

        for item in items:
            term = item.Title
            terms.append(SimpleVocabulary.createTerm(term, term, term))

        return SimpleVocabulary(terms)


class ITag(form.Schema):
    """Interface for Tag content type
    """

    title = schema.TextLine(
        title=_(u"Name"),
    )

    description = schema.Text(
        title=_(u"A short summary"),
    )

    picture = NamedImage(
        title=_(u"Picture"),
        description=_(u"Please upload an image"),
        required=False,
    )


@grok.subscribe(ITag, IObjectModifiedEvent)
def object_edited(context, event):
    context.subject = (context.title, )


@grok.subscribe(ITag, IObjectAddedEvent)
def object_added(context, event):
    context.subject = (context.title, )


@grok.subscribe(ITag, IObjectRemovedEvent)
def object_deleted(context, event):
    # First time it's called, before the "delete or no" popup
    if(context.REQUEST.method == 'GET'):
        pass
    # Second and third time it's called, after popup
    elif(context.REQUEST.method == 'POST'):
        try:
            context.REQUEST.form['form.submitted']
            # Second time
        except:
            # Third time
            catalog = api.portal.get_tool(name='portal_catalog')
            all_tags = [i.getObject() for i in catalog(Subject={
                'query': (context.title, ),
                'operator': 'and',
            })]
            for item in all_tags:
                item.setSubject(tuple((
                    i for i in item.Subject() if i != context.title
                )
                ))


class View(grok.View):
    grok.context(ITag)
    grok.require('zope2.View')

    def articles(self):
        """Return a catalog search result of articles that have this tag
        """

        catalog = api.portal.get_tool(name='portal_catalog')
        all_articles = catalog(portal_type="tribuna.content.article")

        return [article for article in all_articles
                if article.review_state == 'published']
