from Acquisition import aq_inner
from BTrees.OOBTree import OOBTree
from cStringIO import StringIO
from gzip import GzipFile
from plone import api
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.sitemap.sitemap import _render_cachekey
from plone.memoize import ram
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import SitemapQueryBuilder
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.publisher.interfaces import NotFound

from tribuna.content.config import SITEMAP_SETTINGS
from tribuna.content.interfaces import ISiteMap


class CatalogSiteMap(BrowserView):
    implements(ISiteMap)

    def siteMap(self):
        root = api.portal.get()
        root_url = root.absolute_url()
        context = aq_inner(root)
        data = {'children': []}

        strategy = getMultiAdapter((context, self), INavtreeStrategy)

        for q, r, pt in SITEMAP_SETTINGS:

            queryBuilder = SitemapQueryBuilder(context)
            query = queryBuilder()
            query['path']['query'] += q
            query['portal_type'] = pt

            root_del = root_url + q
            root_replace = root_url + r

            tmp_data = buildFolderTree(context, obj=context,
                                       query=query, strategy=strategy)

            tmp_data['children'][0]['absolute_url'] = (
                root_replace +
                tmp_data['children'][0]['absolute_url'][len(root_del):]
            )
            tmp_data['children'][0]['getURL'] = (
                root_replace +
                tmp_data['children'][0]['getURL'][len(root_del):]
            )

            for child in tmp_data['children'][0]['children']:
                child['children'] = []
                child['absolute_url'] = (root_replace +
                                         child['absolute_url'][len(root_del):])
                child['getURL'] = (root_replace +
                                   child['getURL'][len(root_del):])

            data['children'].extend(tmp_data['children'])

        return data


class SiteMapView(BrowserView):
    """Creates the sitemap as explained in the specifications.

    http://www.sitemaps.org/protocol.php
    """

    template = ViewPageTemplateFile('sitemap_templates/sitemap.xml')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.root = api.portal.get()
        self.filename = 'sitemap.xml.gz'

    def objects(self):
        """Returns the data to create the sitemap."""
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {}
        root_url = self.root.absolute_url()

        ptool = getToolByName(self, 'portal_properties')
        siteProperties = getattr(ptool, 'site_properties')
        typesUseViewActionInListings = frozenset(
            siteProperties.getProperty('typesUseViewActionInListings', [])
        )

        is_plone_site_root = IPloneSiteRoot.providedBy(self.root)
        query['path'] = '/'.join(self.root.getPhysicalPath())

        query['is_default_page'] = True
        default_page_modified = OOBTree()
        for item in catalog.searchResults(query, Language='all'):
            key = item.getURL().rsplit('/', 1)[0]
            value = (item.modified.micros(), item.modified.ISO8601())
            default_page_modified[key] = value

        # The plone site root is not catalogued.
        if is_plone_site_root:
            loc = self.root.absolute_url()
            date = self.root.modified()
            # Comparison must be on GMT value
            modified = (date.micros(), date.ISO8601())
            default_modified = default_page_modified.get(loc, None)
            if default_modified is not None:
                modified = max(modified, default_modified)
            lastmod = modified[1]
            yield {
                'loc': loc,
                'lastmod': lastmod,
                #'changefreq': 'always',
                # hourly/daily/weekly/monthly/yearly/never
                #'prioriy': 0.5, # 0.0 to 1.0
            }

        query['is_default_page'] = False
        for p, r, pt in SITEMAP_SETTINGS:
            query['path'] = '/'.join(self.root.getPhysicalPath()) + p
            query['portal_type'] = pt[0]

            root_del = root_url + p
            root_replace = root_url + r

            for item in catalog.searchResults(query, Language='all'):
                loc = item.getURL()
                date = item.modified

                loc = root_replace + loc[len(root_del):]

                # Comparison must be on GMT value
                modified = (date.micros(), date.ISO8601())
                default_modified = default_page_modified.get(loc, None)
                if default_modified is not None:
                    modified = max(modified, default_modified)
                lastmod = modified[1]
                if item.portal_type in typesUseViewActionInListings:
                    loc += '/view'
                yield {
                    'loc': loc,
                    'lastmod': lastmod,
                    #'changefreq': 'always',
                    # hourly/daily/weekly/monthly/yearly/never
                    #'prioriy': 0.5, # 0.0 to 1.0
                }

    @ram.cache(_render_cachekey)
    def generate(self):
        """Generates the Gzipped sitemap."""
        xml = self.template()
        fp = StringIO()
        gzip = GzipFile(self.filename, 'w', 9, fp)
        gzip.write(xml)
        gzip.close()
        data = fp.getvalue()
        fp.close()
        return data

    def __call__(self):
        """Checks if the sitemap feature is enable and returns it."""
        sp = getToolByName(self.root, 'portal_properties').site_properties
        if not sp.enable_sitemap:
            raise NotFound(self.root, self.filename, self.request)

        self.request.response.setHeader('Content-Type',
                                        'application/octet-stream')
        return self.generate()
