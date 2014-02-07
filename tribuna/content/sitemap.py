from Acquisition import aq_inner
from plone import api
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree
from Products.CMFPlone.browser.navtree import SitemapQueryBuilder
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.interface import implements

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
