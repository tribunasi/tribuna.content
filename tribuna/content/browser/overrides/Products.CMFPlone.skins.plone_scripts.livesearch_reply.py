## Script (Python) "livesearch_reply"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=q,limit=10,path=None
##title=Determine whether to show an id in an edit form
##

"""A customization of Plone script to change the item URL, so we redirect
to articles/some-article-id instead of the article default view.

XXX: this customization won't be needed if we do a custom traverser for
articles.
"""
view = context.restrictedTraverse('@@live-search')
#import pdb;pdb.set_trace()
foo = view.search(q, limit=limit, path=path)
#foo = """
#<fieldset class="livesearchContainer">\n<legend id="livesearchLegend">\xc5\xbdivo iskanje &#8595;</legend>\n<div class="LSIEFix">\n<ul class="LSTable">\n<li class="LSRow">\n<img width="16" height="16" src="http://localhost:8080/Tribuna/user.gif" alt="Tekst object code" />\n<a href="http://localhost:8080/Tribuna/articles/foooo" title="foooo" class="contenttype-tribuna-content-article">foooo</a>\n<div class="LSDescr"></div>\n</li>\n<li class="LSRow">\n<a href="http://localhost:8080/Tribuna/@@search" class="advancedsearchlink">Napredno Iskanje...</a>\n</li>\n</ul>\n</div>\n</fieldset>
#"""
return foo
