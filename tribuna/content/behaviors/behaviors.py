"""Behaviours to assign tags (to ideas).

Includes a form field and a behaviour adapter that stores the data in the
standard Subject field.
"""


from collective.miscbehaviors.behavior.utils import context_property
from collective.z3cform.widgets.token_input_widget import TokenInputFieldWidget
from plone import api
from plone.dexterity.interfaces import IDexterityContent
from plone.directives import form
from plone.indexer.decorator import indexer
from plone.namedfile import field as namedfile
from Products.CMFCore.interfaces import IDublinCore
from rwproperty import getproperty, setproperty
from tribuna.content import _
from tribuna.content.utils import our_unicode
from tribuna.content.utils import TagsListHighlighted
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides
from zope.interface import implements


class ITermitnjakLeadImage(form.Schema):
    """Add tags to content."""

    image = namedfile.NamedBlobImage(
        title=_(u"Lead Image"),
        description=u""
    )

alsoProvides(ITermitnjakLeadImage, form.IFormFieldProvider)


class TermitnjakLeadImage(object):
    """Adapter for Lead Image."""
    implements(ITermitnjakLeadImage)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    # -*- Your behavior property setters & getters here ... -*-
    imageCaption = context_property('imageCaption')
    image = context_property('image')


class ITags(form.Schema):
    """Auto-complete tags."""

    form.widget(tags_old=CheckBoxFieldWidget)
    tags_old = schema.List(
        title=_(u'Tags'),
        value_type=schema.Choice(source=TagsListHighlighted()),
    )

    form.widget(tags_new=TokenInputFieldWidget)
    tags_new = schema.List(
        title=_(u"Categories"),
        value_type=schema.TextLine(),
        default=[],
        required=False
    )

alsoProvides(ITags, form.IFormFieldProvider)


class Tags(object):
    """Store tags in the Dublin Core metadata Subject field. This makes
    tags easy to search for.
    """
    implements(ITags)
    adapts(IDublinCore)

    def __init__(self, context):
        self.context = context

    @getproperty
    def tags_old(self):
        return set(self.context.Subject())

    @setproperty
    def tags_old(self, value):
        if value is None:
            value = ()
        self.context.setSubject(tuple(value))

    @getproperty
    def tags_new(self):
        return set(self.context.Subject())

    @setproperty
    def tags_new(self, value):

        if value is None:
            value = []

        # Add all tags from 'tags_old' to our values
        value += list(self.context.Subject())

        # Get all 'new' tags
        # XXX
        # FIX
        with api.env.adopt_roles('Site Administrator'):
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

            dict_value = {}
            for it in value:
                foo = our_unicode(it).lower().replace(' ', '')
                if foo not in dict_value.keys():
                    dict_value[foo] = it

            new_value = []
            added_values = []

            for key, val in dict_value.items():
                if key in titles.keys():
                    new_value.append(titles[key])
                else:
                    new_value.append(val)
                    added_values.append(val)

        self.context.setSubject(tuple(new_value))
        site = api.portal.get()
        for title in added_values:
            obj = api.content.create(
                type='tribuna.content.tag',
                title=title,
                description="",
                highlight_in_navigation=False,
                container=site['tags'])
            api.content.transition(obj=obj, transition='submit')


class ILockOnHomePage(form.Schema):
    """Behavior for locking our content item on home page."""

    locked_on_home = schema.Bool(
        title=_(u"Is article locked on first page?"),
        required=True,
    )

alsoProvides(ILockOnHomePage, form.IFormFieldProvider)


class LockOnHomePage(object):
    """Adapter for LockOnHomePage."""
    implements(ILockOnHomePage)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    # -*- Your behavior property setters & getters here ... -*-
    locked_on_home = context_property('locked_on_home')


@indexer(ILockOnHomePage)
def lock_on_home_page_indexer(obj):
    """ """
    return obj.locked_on_home
