from marshmallow import Schema, fields, validate

class WorkingModel(Schema):
    str = fields.String(validate=validate.Length(max=5, error='String is too long'))

class NonWorkingModel(Schema):
    str = fields.String(
        load_from='sample_string',
        dump_to='SampleString',
        validate=validate.Length(max=5, error='String is too long')
    )

working_model = WorkingModel()
working_obj = {'str': '123456'}
errors = working_model.validate(working_obj)
print errors
# Output:
# {'str': ['String is too long']}


non_working_model = NonWorkingModel()
non_working_obj = {'sample_string': '123456'}
errors = non_working_model.validate(non_working_obj)
print errors
obj = non_working_model.dump(non_working_obj)
print obj.data
print obj.errors
print "===="
obj2 = non_working_model.load(non_working_obj)
print obj2.errors
print obj2.data
# Output:
# {}

from invoices_record_models import IdentificacionFactura
from datetime import datetime
m = IdentificacionFactura()
obj = {
        'FechaExpedicionFacturaEmisor': datetime.strptime(
            '2016-03-25', '%Y-%m-%d'
        )
    }
dumbo = m.dump(
    obj
)
errors = m.validate(obj)
print dumbo.data
