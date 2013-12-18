from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.utils import safe_unicode
from Products.PythonScripts.standard import url_quote_plus
from Products.PythonScripts.standard import html_quote
from five import grok
#from Products import AdvancedQuery
from zope.interface import Interface

from tribuna.content.utils import our_unicode
from tribuna.content.utils import prepare_search_string


class LiveSearchView(grok.View):
    grok.context(Interface)
    grok.name('livesearch')
    grok.require('zope2.View')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.output = []

    def write(self, s):
        self.output.append(safe_unicode(s))

    def render(self):
        q = self.request.form.get('q', '')
        limit = self.request.form.get('limit', 10)
        path = self.request.form.get('path')
        return self.search(q, limit=limit, path=path)

    def search(self, q, limit=10, path=None):

        results = search_catalog_results(self.context, q, limit, path)
        return self.render_livesearch_box(q, path, limit, results)

    def render_livesearch_box(self, q, path, limit, results):
        ts = getToolByName(self.context, 'translation_service')
        portal_url = getToolByName(self.context, 'portal_url')()
        plone_view = self.context.restrictedTraverse('@@plone')
        #portal_state = self.context.restrictedTraverse('@@plone_portal_state')
        portalProperties = getToolByName(self.context, 'portal_properties')
        siteProperties = getattr(portalProperties, 'site_properties', None)
        ploneUtils = getToolByName(self.context, 'plone_utils')
        useViewAction = []
        if siteProperties is not None:
            useViewAction = siteProperties.getProperty(
                                'typesUseViewActionInListings', [])

        #searchterm_query = '?searchterm=%s' % url_quote_plus(q)
        pretty_title_or_id = ploneUtils.pretty_title_or_id
        searchterms = url_quote_plus(q)

        # SIMPLE CONFIGURATION
        #USE_ICON = True
        MAX_TITLE = 50
        MAX_DESCRIPTION = 150

        REQUEST = self.request
        RESPONSE = REQUEST.RESPONSE
        RESPONSE.setHeader('Content-Type', 'text/xml;charset=utf-8')

        # replace named entities with their numbered counterparts, in the xml the named
        # ones are not correct
        #   &darr;      --> &#8595;
        #   &hellip;    --> &#8230;
        legend_livesearch = _('legend_livesearch', default='LiveSearch &#8595;')
        label_no_results_found = _('label_no_results_found',
                                   default='No matching results found.')
        label_advanced_search = _('label_advanced_search',
                                  default='Advanced Search&#8230;')
        label_show_all = _('label_show_all', default='Show all items')

        if not results:
            self.write('''<fieldset class="livesearchContainer">''')
            self.write('''<legend id="livesearchLegend">%s</legend>'''
                    % ts.translate(legend_livesearch, context=REQUEST))
            self.write('''<div class="LSIEFix">''')
            self.write('''<div id="LSNothingFound">%s</div>'''
                    % ts.translate(label_no_results_found, context=REQUEST))
            self.write('''<div class="LSRow">''')
            self.write('<a href="%s" class="advancedsearchlink">%s</a>' %
                    (portal_url + '/@@search',
                    ts.translate(label_advanced_search, context=REQUEST)))
            self.write('''</div>''')
            self.write('''</div>''')
            self.write('''</fieldset>''')
        else:
            self.write('''<fieldset class="livesearchContainer">''')
            self.write('''<legend id="livesearchLegend">%s</legend>'''
                    % ts.translate(legend_livesearch, context=REQUEST))
            self.write('''<div class="LSIEFix">''')
            self.write('''<ul class="LSTable">''')
            for result in results[:limit]:
                icon = plone_view.getIcon(result)
                # XXX: default item URL
                # itemUrl = result.getURL()
                itemUrl = "{0}/articles/{1}".format(
                    self.context.absolute_url(), str(result.id))
                if result.portal_type in useViewAction:
                    itemUrl += '/view'

                #itemUrl = itemUrl + searchterm_query

                self.write('''<li class="LSRow">''')
                self.write(icon.html_tag() or '')
                full_title = safe_unicode(pretty_title_or_id(result))
                if len(full_title) > MAX_TITLE:
                    display_title = ''.join((full_title[:MAX_TITLE], '...'))
                else:
                    display_title = full_title

                full_title = full_title.replace('"', '&quot;')
                klass = 'contenttype-%s' \
                            % ploneUtils.normalizeString(result.portal_type)
                self.write('''<a href="%s" title="%s" class="%s">%s</a>'''
                        % (itemUrl, full_title, klass, display_title))
                display_description = safe_unicode(result.Description)
                if len(display_description) > MAX_DESCRIPTION:
                    display_description = ''.join(
                        (display_description[:MAX_DESCRIPTION], '...'))

                # need to quote it, to avoid injection of html containing javascript
                # and other evil stuff
                display_description = html_quote(display_description)
                self.write('''<div class="LSDescr">%s</div>''' % (display_description))
                self.write('''</li>''')
                full_title, display_title, display_description = None, None, None

            self.write('''<li class="LSRow">''')
            self.write('<a href="%s" class="advancedsearchlink">%s</a>' %
                    (portal_url + '/@@search',
                    ts.translate(label_advanced_search, context=REQUEST)))
            self.write('''</li>''')

            if len(results) > limit:
                # add a more... row
                self.write('''<li class="LSRow">''')
                searchquery = '@@search?SearchableText=%s&path=%s' \
                                % (searchterms, path)
                self.write('<a href="%s" class="advancedsearchlink">%s</a>' % (
                                     searchquery,
                                     ts.translate(label_show_all, context=REQUEST)))
                self.write('''</li>''')

            self.write('''</ul>''')
            self.write('''</div>''')
            self.write('''</fieldset>''')

        return '\n'.join(self.output).encode('utf-8')



def search_catalog_results(context, q, limit, path):
    ploneUtils = getToolByName(context, 'plone_utils')

    # generate a result set for the query
    catalog = context.portal_catalog

    friendly_types = ploneUtils.getUserFriendlyTypes()

    # for now we just do a full search to prove a point, this is not the
    # way to do this in the future, we'd use a in-memory probability based
    # result set.
    # convert queries to zctextindex

    # XXX really if it contains + * ? or -
    # it will not be right since the catalog ignores all non-word
    # characters equally like
    # so we don't even attept to make that right.
    # But we strip these and these so that the catalog does
    # not interpret them as metachars
    # See http://dev.plone.org/plone/ticket/9422 for an explanation of '\u3000'

    q = our_unicode(q)
    r = prepare_search_string(q)

    params = {
        'SearchableText': r,
        'portal_type': friendly_types,
        'sort_limit': limit + 1,
        'review_state': "published",
    }
    params2 = {
        'Subject': q,
        'portal_type': friendly_types,
        'sort_limit': limit + 1,
        'review_state': "published",
    }

    if path is None:
        # useful for subsites
        params2['path'] = params['path'] = getNavigationRoot(context)
    else:
        params2['path'] = params['path'] = path

    # We join the results of both queries and get rid of duplicates (duplicates
    # can appear when the query is found both in text and in Subject). The
    # original idea was to convert them to sets, but this doesn't work as the
    # brain items aren't equivalent. One possibility would be to get all
    # objects (then sets would work), or we manually get rid of duplicates
    # (based on ID's)
    results1 = catalog(**params)
    results2 = catalog(**params2)
    results = []
    result_ids = []
    for brain in results1 + results2:
        if brain.id not in result_ids:
            results.append(brain)
            result_ids.append(brain.id)

    return results
