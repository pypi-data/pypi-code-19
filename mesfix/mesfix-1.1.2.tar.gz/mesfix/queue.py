import pika
import json
import pprint


def accept_contracts(entity_object):
    message = {
        'entity': {
            'email': entity_object.email,
            'id': entity_object.id
        }
    }

    return message


def validate_documents(entity_object):
    message = {
        'entity': {
            'email': entity_object.email,
            'id': entity_object.id
        }
    }

    return message


def upload_documents(entity_object, document_object):
    message = {
        'entity': {
            'email': entity_object.email,
            'firstName': entity_object.first_name,
            'lastName': entity_object.last_name,
            'typeUser': entity_object.user_type,
            'id': entity_object.id
        },
        'document': {
            'type': document_object.type,
            'id': document_object.id,
            'link': document_object.link
        }
    }

    return message


def ofac_user(entity_object):
    message = {
        'entity': {
            'email': entity_object.email,
            'document': {
                'type': entity_object.entity_document.document_type,
                'id': entity_object.entity_document.document_id
            },
            'firstName': entity_object.first_name,
            'lastName': entity_object.last_name,
            'address': entity_object.address,
            'phone': entity_object.phone
        }
    }

    return message


def service_error(error_object):
    message = {
        'error': {
            'message': error_object.message,
            'procedure': error_object.procedure,
            'method': error_object.method,
            'code': error_object.code,
            'route': error_object.route
        },
        'logger': {
            'name': error_object.logger_name,
            'level': error_object.logger_level
        }
    }

    return message


def missing_documents(user_account_object, entity_object, company_object, document_objects):
    message = {
        'type_account': user_account_object.type_account,
        'type_user': user_account_object.type_user,
        'name': entity_object.first_name + ' ' + entity_object.last_name,
        'email': entity_object.email,
        'company_name': company_object.name,
        'documents': [document.name for document in document_objects]
    }

    return message


def access_update(user_account_object, entity_object, company_object):
    message = {
        'type_account': user_account_object.type_account,
        'type_user': user_account_object.type_user,
        'name': entity_object.first_name + ' ' + entity_object.last_name,
        'email': entity_object.email,
        'company_name': company_object.name
    }

    return message


def confirmed_payment_seller(user_account_object, entity_object, company_object, auction_object):
    message = {
        'type_account': user_account_object.type_account,
        'type_user': user_account_object.type_user,
        'entity': {
            'user': {
                'email': entity_object.email,
                'firstName': entity_object.first_name,
                'lastName': entity_object.last_name
            },
            'company': {
                'name': company_object.name
            }
        },
        'auction': {
            'id': auction_object.id,
            'due_date': auction_object.due_date,
            'transaction': {
                'value': auction_object.auction_transaction_object.value
            }
        }
    }

    return message


def confirmed_payment(user_account_object, entity_object, company_object, auction_object):
    message = {
        'type_account': user_account_object.type_account,
        'type_user': user_account_object.type_user,
        'entity': {
            'user': {
                'email': entity_object.email,
                'firstName': entity_object.first_name,
                'lastName': entity_object.last_name
            },
            'company': {
                'name': company_object.name
            }
        },
        'auction': {
            'id': auction_object.id,
        }
    }

    return message


def update_bid(user_account_object, entity_object, company_object, auction_object, link_object):
    message = {
        'type_account': user_account_object.type_account,
        'type_user': user_account_object.type_user,
        'entity': {
            'user': {
                'email': entity_object.email,
                'firstName': entity_object.first_name,
                'lastName': entity_object.last_name
            },
            'company': {
                'name': company_object.name
            }
        },
        'auction': {
            'id': auction_object.id,
            'annual_yield': auction_object.annual_yield,
            'transaction': {
                'value': auction_object.auction_transaction_object.value
            }
        },
        'link': link_object.link
    }

    return message


def auction_bid(user_account_object, offer_object, document_objects,
                acceptor_object, seller_object, investor_entity_object, company_object, auction_object):
    message = {
        'type_account': user_account_object.type_account,
        'type_user': user_account_object.type_user,
        'net_value': offer_object.net_value,
        'bid_id': offer_object.offer_id,
        'offerted_value': offer_object.offered_value,
        'auction_due_date': offer_object.due_date,
        'payment_date': offer_object.payment_date,
        'rent_neta': offer_object.profitability,
        'invoices': [document.name for document in document_objects],
        'acceptor': acceptor_object.string,
        'seller': seller_object.string,
        'investor': {
            'user': {
                'name': investor_entity_object.first_name + ' ' + investor_entity_object.last_name,
                'email': investor_entity_object.email
            },
            'company': {
                'name': company_object.name
            }
        },
        'auction': {
            'id': auction_object.id
        }
    }

    return message


def investment_certificate(user_account_object, entity_object, company_object, link_object, string_object):
    message = {
        'type_account': user_account_object.type_account,
        'type_user': user_account_object.type_user,
        'email': entity_object.email,
        'investor_name': entity_object.first_name + ' ' + entity_object.last_name,
        'company_name': company_object.name,
        'url_file': link_object.link,
        'notice': string_object.string
    }

    return message


def end_auction(user_account_object, offer_object, document_objects,
                acceptor_object, seller_object, investor_entity_object, company_object, link_object):
    message = {
        'type_account': user_account_object.type_account,
        'type_user': user_account_object.type_user,
        'net_value': offer_object.net_value,
        'offerted_value': offer_object.offered_value,
        'auction_due_date': offer_object.due_date,
        'payment_date': offer_object.payment_date,
        'rent_neta': offer_object.profitability,
        'invoices': [document.name for document in document_objects],
        'acceptor': acceptor_object.string,
        'seller': seller_object.string,
        'id_oferta': offer_object.offer_id,
        'investor': {
            'account_user': {
                'name': investor_entity_object.first_name + ' ' + investor_entity_object.last_name,
                'email': investor_entity_object.email
            },
            'company': {
                'name': company_object.name
            }
        },
        'link': link_object.link
    }

    return message


def transaction_received(user_account_object, entity_object, company_object, auction_object):
    message = {
        'type_account': user_account_object.type_account,
        'type_user': user_account_object.type_user,
        'name': entity_object.first_name + ' ' + entity_object.last_name,
        'companyName': company_object.name,
        'email': entity_object.email,
        'auctionNumber': auction_object.id,
        'value': auction_object.auction_transaction_object.value
    }

    return message

class MesfixRabbitMQConnector(object):
    ROUTING_KEYS = [

        # OG_signup
        "signup"

        # OG_accept_contracts
        "acceptContracts",

        # OA_validate_user_documents                
        "validateDocuments",

        # OG_upload_documents-ms            
        "uploadDocument",

        # OG_signup             
        "ofacUser",

        # OG_admin / OG_signup / OS_relation / OG_edit_profile-ms / OG_profile_info-ms / 
        # OS_auction_details-ms / OS_upload_invoice-ms / OG_DW_WS-develop / OG_upload_documents-ms
        "serviceError",

        # php front                 
        "presignup",

        # php front                 
        "register-verified",

        # OG_admin
        "missing-documents",

        # OG_admin / php front          
        "access-update",

        # php front  
        "missing-auctions-documents",

        # php front  
        "relations-verified",

        # OI_auctions_summary
        "confirmed-payment-seller",

        # OI_auctions_summary
        "confirmed-payment",

        # OI_auctions_summary
        "update-bid",

        #
        "payment-payers",

        # OI_auctions_summary
        "auction-bid",

        #
        "auction-accept",

        # OG_admin
        "investment-certificate",

        #
        "investment-report",

        # php front
        "forgot",

        # php front  
        "auction-active",

        # OS_end_auction-develop / OS_auction_details / php front  
        "end-auction",

        #                   
        "notice-auction",

        # php front  
        "notificationInvestorsPaid",

        # php front  
        "payment-notice",

        # OI_auctions_summary
        "transaction-received",

        # OI_auctions_summary
        "makeBid"
    ]

    def __init__(self, rabbit_user, rabbit_password, rabbit_host, rabbit_exchange, rabbit_type):
        self.rabbit_user = rabbit_user
        self.rabbit_password = rabbit_password
        self.rabbit_host = rabbit_host
        self.rabbit_exchange = rabbit_exchange
        self.rabbit_type = rabbit_type

    def publish_message(self, routing_key, message):
        user, pswd = self.rabbit_user, self.rabbit_password
        credentials = pika.PlainCredentials(user, pswd)

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.rabbit_host, credentials=credentials))

        message = json.dumps(message)
        channel = connection.channel()
        channel.exchange_declare(exchange=self.rabbit_exchange, type=self.rabbit_type)
        channel.basic_publish(exchange=self.rabbit_exchange, routing_key=routing_key, body=message)

    def message_publisher_factory(self, routing_key, **kargs):
        log_message = kargs.get("log")
        link_object = kargs.get("link")
        user_object = kargs.get("user")
        error_object = kargs.get("error")
        offer_object = kargs.get("offer")
        entity_object = kargs.get("entity")
        string_object = kargs.get("string")
        seller_object = kargs.get("seller")
        profile_object = kargs.get("profile")
        auction_object = kargs.get("auction")
        company_object = kargs.get("company")
        acceptor_object = kargs.get("acceptor")
        document_object = kargs.get("document")
        document_objects = kargs.get("documents")
        user_account_object = kargs.get("account")
        investor_entity_object = kargs.get("investor")

        message = ''

        if routing_key == 'acceptContracts':
            message = accept_contracts(entity_object)

        if routing_key == 'validateDocuments':
            message = validate_documents(entity_object)

        if routing_key == 'uploadDocument':
            message = upload_documents(entity_object, document_object)

        if routing_key == 'ofacUser':
            message = ofac_user(entity_object)

        if routing_key == 'serviceError':
            message = service_error(error_object)

        if routing_key == 'missing-documents':
            message = missing_documents(user_account_object, entity_object, company_object,
                                        document_objects)

        if routing_key == 'access-update':
            message = access_update(user_account_object, entity_object, company_object)

        if routing_key == 'confirmed-payment-seller':
            message = confirmed_payment_seller(user_account_object, entity_object, company_object,
                                               auction_object)

        if routing_key == 'confirmed-payment':
            message = confirmed_payment(user_account_object, entity_object, company_object,
                                        auction_object)

        if routing_key == 'update-bid':
            message = update_bid(user_account_object, entity_object, company_object,
                                 auction_object, link_object)

        if routing_key == 'auction-bid':
            message = auction_bid(user_account_object, offer_object, document_objects,
                                  acceptor_object, seller_object, investor_entity_object, company_object,
                                  auction_object)

        if routing_key == 'investment-certificate':
            message = investment_certificate(user_account_object, entity_object, company_object,
                                             link_object, string_object)

        if routing_key == 'end-auction':
            message = end_auction(user_account_object, offer_object, document_objects, acceptor_object,
                                  seller_object, investor_entity_object, company_object, link_object)

        if routing_key == 'transaction-received':
            message = transaction_received(user_account_object, entity_object, company_object, auction_object)

        if routing_key == 'log':
            message = log_message

        pprint.pprint(message)
        self.publish_message(routing_key, message)

        return message
