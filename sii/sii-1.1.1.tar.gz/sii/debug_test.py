from sii.resource import SII
from sii.models.invoices_record import CRE_FACTURAS_EMITIDAS
from expects import *
from spec.testing_data import DataGenerator

# data_gen = DataGenerator()
# invoice = data_gen.get_out_invoice()
# invoice_obj = SII.generate_object(invoice)
# cabecera = (
#     invoice_obj['SuministroLRFacturasEmitidas']['Cabecera']
# )

import os
from expects import *

os.environ['NIF_TITULAR'] = 'ES11111111T'
os.environ['NIF_CONTRAPARTE'] = 'esES654321P'
new_data_gen = DataGenerator()
nifs_test_invoice = new_data_gen.get_out_invoice()
nif_invoice = nifs_test_invoice.company_id.partner_id.vat


nifs_test_obj = SII.generate_object(nifs_test_invoice)
nif_generated = nifs_test_obj['SuministroLRFacturasEmitidas']['Cabecera']['Titular']['NIF']

expect(nif_generated).to(equal(nif_invoice))

expect(
    nifs_test_obj['SuministroLRFacturasEmitidas']
    ['RegistroLRFacturasEmitidas']['FacturaExpedida']
    ['Contraparte']['NIF']
).to(
    equal(nifs_test_invoice.company_id.partner_id.vat[2:])
)
