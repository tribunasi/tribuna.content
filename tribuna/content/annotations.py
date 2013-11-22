"""Integration code for tribuna.annotator"""

from five import grok
from plone import api
from zope.lifecycleevent.interfaces import IObjectCreatedEvent

from tribuna.annotator.utils import unrestricted_create
from tribuna.annotator.annotation import IAnnotation
from tribuna.content.utils import our_unicode


@grok.subscribe(IAnnotation, IObjectCreatedEvent)
def create_annotation_tags(obj, event):
    # Get all 'new' tags
    # XXX: Fix so we don't need to use a custom Plone user (bug in
    # plone.api)
    with api.env.adopt_user('tags_user'):
        catalog = api.portal.get_tool(name='portal_catalog')
        items = catalog({
            'portal_type': 'tribuna.content.tag',
        })

    # Compare tags with the one already in our system, if they're the
    # "same" (lower and ignore spaces), use those tags
    titles = dict(
        (our_unicode(it.Title).lower().replace(' ', ''), it.Title)
        for it in items
    )

    tags = obj.Subject()
    dict_tags = {}
    for it in tags:
        foo = our_unicode(it).lower().replace(' ', '')
        if foo not in dict_tags.keys():
            dict_tags[foo] = it

    new_tags = []
    added_tags = []

    for key, val in dict_tags.items():
        if key in titles.keys():
            new_tags.append(our_unicode(titles[key]))
        else:
            new_tags.append(our_unicode(val))
            added_tags.append(our_unicode(val))

    site = api.portal.get()
    for title in added_tags:
        unrestricted_create(
            portal_type='tribuna.content.tag',
            title=title,
            description="",
            highlight_in_navigation=False,
            container=site['tags-folder'],
            transition='submit')

    with api.env.adopt_user('tags_user'):
        obj.setSubject(tuple(new_tags))
