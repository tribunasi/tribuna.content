"""Behaviours to assign tags (to ideas).

Includes a form field and a behaviour adapter that stores the data in the
standard Subject field.
"""

# from rwproperty import getproperty, setproperty
from collective.miscbehaviors.behavior.utils import context_property
from plone.dexterity.interfaces import IDexterityContent
from plone.directives import form
from plone.indexer.decorator import indexer
from plone.namedfile import field as namedfile
from zope import schema
from zope.component import adapts
from zope.interface import implements, alsoProvides
from five import grok

from tribuna.content import _


class ITermitnjakLeadImage(form.Schema):
    """Add tags to content
    """

    image = namedfile.NamedBlobImage(
        title=_(u"Lead Image"),
        description=u"",
        required=True,
    )

    imageCaption = schema.TextLine(
        title=_(u"Lead Image Caption"),
        description=u"",
        required=True,
    )

alsoProvides(ITermitnjakLeadImage, form.IFormFieldProvider)


class TermitnjakLeadImage(object):
    """
       Adapter for Lead Image
    """
    implements(ITermitnjakLeadImage)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    # -*- Your behavior property setters & getters here ... -*-
    imageCaption = context_property('imageCaption')
    image = context_property('image')


class ILockOnHomePage(form.Schema):
    """Behavior for locking our content item on home page
    """

    locked_on_home = schema.Bool(
        title=_(u"Is article locked on first page?")
    )

alsoProvides(ILockOnHomePage, form.IFormFieldProvider)


class LockOnHomePage(object):
    """
       Adapter for LockOnHomePage
    """
    implements(ILockOnHomePage)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

    # -*- Your behavior property setters & getters here ... -*-
    locked_on_home = context_property('locked_on_home')


@indexer(ILockOnHomePage)
def lock_on_home_page_indexer(obj):
    """
    """
    return obj.locked_on_home

