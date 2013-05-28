from plone.api.portal import get_tool


def TagsPublished():
    catalog = get_tool(name='portal_catalog')
    tags = tuple(i.Title for i in catalog(
        portal_type='tribuna.content.tag',
        review_state='published',
    ))
    return tags
