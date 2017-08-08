import grako
grammar=open('parser.ebnf').read()
model = grako.genmodel("all", grammar)
print(model.parse('a:"2"',start='cuts'))
