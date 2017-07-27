# coding=utf-8
from marshmallow import fields, Schema, validate
from sii import invoices_record_models

class SingleModel(Schema):
    str = fields.String(validate=validate.Length(max=5, error='STRING MASSSA LLARG COLLONS'))

new_model = SingleModel()
new_obj = {'str': '123456'}
errors = new_model.validate(new_obj)
print '\n\n\n************* Errors SINGLE MODEL 1: ', errors
print '\n'
print '========================='
print 'EL SINGLE MODEL 1 de ejemplo es:\n'
from pprintpp import pprint
single_model_dump = new_model.dump(new_obj)
pprint(new_model.load(new_obj).data)
# pprint(single_model_dump.data)
print '========================='


new_obj2 = {'str': '123'}
errors = new_model.validate(new_obj2)
print '\n\n\n************* Errors SINGLE MODEL 2: ', errors
print '\n'
print '========================='
print 'EL SINGLE MODEL 2 de ejemplo es:\n'
from pprintpp import pprint
single_model_dump = new_model.dump(new_obj2)
pprint(new_model.load(new_obj2).data)
pprint(single_model_dump.data)
print '========================='

titular = {
    'NombreRazon': 'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww',
}
titular_model = invoices_record_models.Titular()
errors = titular_model.validate(titular)
print '\n\n\n************* Errors TITULAR MODEL: ', errors
print '\n'
print '========================='
print 'EL TITULAR de ejemplo es:\n'
titular_dump = titular_model.dump(titular)
pprint(titular_dump.data)
print '========================='


class BlobSchema(Schema):
    chunks = fields.List(fields.String)

schema = BlobSchema()
obj = {
    'chunks': [
        'hola', 'adeu'
    ]
}
print '*********************'
print pprint(schema.dump(obj).data)
