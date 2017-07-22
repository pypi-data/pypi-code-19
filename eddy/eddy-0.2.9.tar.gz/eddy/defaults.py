#muh templates
SITE_TEMPLATE = "default"
TEMPLATE = "main"
#pass these to jinja so you can use them in your templates
JINJA_FUNCTIONS = {"zip": zip, "print": print}

#stilistic concers
STYLE = "default"
#only works when "markdown.extensions.codehilite" is enabled
COLORSCHEME = "monokai"

#extensions
EXTENSIONS : dict = {
    #check https://pythonhosted.org/Markdown/extensions/ for a complete list of these
    'MDReader': ["markdown.extensions.codehilite"],
    #none supported for now
    'RSTReader': [],
}

#You can write your own reader. One day I might write documentation for that TODO
READERS : list = []

#authors
#list of authors
AUTHORS = ['me']
# generate pages for authors you'll need to supply and authors.html template
AUTHOR_PAGE = False #not implemented


#output settings
#create index.html. You will have to supply and index.html template
INDEX = True  #not implemented
PDF = False     #generate a pdf of your webpages, result quality may vary. Not implemented TODO

#your site domain. Example: user.github.io/my_blog/  <- '/' is important
URL = ""
