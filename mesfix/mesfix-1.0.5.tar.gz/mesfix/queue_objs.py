class EntityDocumentObject(object):
    def __init__(self, document_type='', document_id=''):
        self.document_type = document_type
        self.document_id = document_id


class EntityObject(object):
    def __init__(self, object_id='', email='', first_name='', last_name='',
                 user_type='', entity_document='', address='', phone=''):
        self.id = object_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.user_type = user_type
        self.entity_document = entity_document
        self.address = address
        self.phone = phone


class CompanyObject(object):
    def __init__(self, object_id='', email='', name='',
                 entity_document='', address='', phone=''):
        self.id = object_id
        self.email = email
        self.name = name
        self.entity_document = entity_document
        self.address = address
        self.phone = phone


class DocumentObject(object):
    def __init__(self, object_id='', object_type='', link='', name=''):
        self.id = object_id
        self.type = object_type
        self.link = link
        self.name = name


class UserAccountObject(object):
    def __init__(self, object_id='', type_account='', type_user=''):
        self.id = object_id
        self.type_account = type_account
        self.type_user = type_user


class ErrorObject(object):
    def __init__(self, message='', procedure='', method='', code='',
                 route='', logger_name='', logger_level=''):
        self.message = message
        self.procedure = procedure
        self.method = method
        self.code = code
        self.route = route
        self.logger_name = logger_name
        self.logger_level = logger_level


class LinkObject(object):
    def __init__(self, link=''):
        self.link = link


class StringObject(object):
    def __init__(self, string=''):
        self.string = string


class AuctionTransactionObject(object):
    def __init__(self, value=''):
        self.value = value


class AuctionBidObject(object):
    def __init__(self, value=''):
        self.value = value


class AuctionObject(object):
    def __init__(self, object_id='', due_date='',
                 auction_transaction_object='', auction_bid_object='', annual_yield=''):
        self.id = object_id
        self.due_date = due_date
        self.annual_yield = annual_yield
        self.auction_transaction_object = auction_transaction_object
        self.auction_bid_object = auction_bid_object


class OfferObject(object):
    def __init__(self, offer_id='', net_value='', offered_value='',
                 due_date='', payment_date='', profitability=''):
        self.offer_id = offer_id
        self.net_value = net_value
        self.offered_value = offered_value
        self.due_date = due_date
        self.payment_date = payment_date
        self.profitability = profitability
