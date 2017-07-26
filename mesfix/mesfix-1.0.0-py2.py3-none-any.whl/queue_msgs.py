def accept_contracts(user_account_object, entity_object):

    message = {
        'contracts': [{
            'account': user_account_object.id
        }],
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
                'document': {
                    'type': entity_object.entity_document.document_type,
                    'id': entity_object.entity_document.document_id
                },
                'firstName': entity_object.first_name,
                'lastName': entity_object.last_name,
                'address': entity_object.address,
                'phone': entity_object.phone
            },
            'company': {
                'email': company_object.email,
                'document': {
                    'type': company_object.entity_document.document_type,
                    'id': company_object.entity_document.document_id
                },
                'name': company_object.name,
                'address': company_object.address,
                'phone': company_object.phone
            }
        },
        'auction': {
            'id': auction_object.id,
            'due_date': auction_object.due_date,
            'annual_yield': auction_object.annual_yield,
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
                'document': {
                    'type': entity_object.entity_document.document_type,
                    'id': entity_object.entity_document.document_id
                },
                'firstName': entity_object.first_name,
                'lastName': entity_object.last_name,
                'address': entity_object.address,
                'phone': entity_object.phone
            },
            'company': {
                'email': company_object.email,
                'document': {
                    'type': company_object.entity_document.document_type,
                    'id': company_object.entity_document.document_id
                },
                'name': company_object.name,
                'address': company_object.address,
                'phone': company_object.phone
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

def update_bid(user_account_object, entity_object, company_object, auction_object):

    message = {
        'type_account': user_account_object.type_account,
        'type_user': user_account_object.type_user,
        'entity': {
            'user': {
                'email': entity_object.email,
                'document': {
                    'type': entity_object.entity_document.document_type,
                    'id': entity_object.entity_document.document_id
                },
                'firstName': entity_object.first_name,
                'lastName': entity_object.last_name,
                'address': entity_object.address,
                'phone': entity_object.phone
            },
            'company': {
                'email': company_object.email,
                'document': {
                    'type': company_object.entity_document.document_type,
                    'id': company_object.entity_document.document_id
                },
                'name': company_object.name,
                'address': company_object.address,
                'phone': company_object.phone
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

def auction_bid(user_account_object, entity_object, company_object, auction_object):

    message = {
        'type_account': user_account_object.type_account,
        'type_user': user_account_object.type_user,
        'entity': {
            'user': {
                'email': entity_object.email,
                'document': {
                    'type': entity_object.entity_document.document_type,
                    'id': entity_object.entity_document.document_id
                },
                'firstName': entity_object.first_name,
                'lastName': entity_object.last_name,
                'address': entity_object.address,
                'phone': entity_object.phone
            },
            'company': {
                'email': company_object.email,
                'document': {
                    'type': company_object.entity_document.document_type,
                    'id': company_object.entity_document.document_id
                },
                'name': company_object.name,
                'address': company_object.address,
                'phone': company_object.phone
            }
        },
        'auction': {
            'id': auction_object.id,
            'due_date': auction_object.due_date,
            'bid': {
                'value': auction_object.auction_bid_object.value
            },
            'transaction': {
                'value': auction_object.auction_transaction_object.value
            }
        }
    }

    return message

def investment_certificate(user_account_object, entity_object, company_object, link_object, string_object):

    message = {
        'type_account': user_account_object.type_account,
        'type_user': user_account_object.type_user,
        'investor': {
            'user': {
                'email': entity_object.email,
                'document': {
                    'type': entity_object.entity_document.document_type,
                    'id': entity_object.entity_document.document_id
                },
                'firstName': entity_object.first_name,
                'lastName': entity_object.last_name,
                'address': entity_object.address,
                'phone': entity_object.phone
            },
            'company': {
                'email': company_object.email,
                'document': {
                    'type': company_object.entity_document.document_type,
                    'id': company_object.entity_document.document_id
                },
                'name': company_object.name,
                'address': company_object.address,
                'phone': company_object.phone
            }
        },
        'url_file': link_object.link,
        'notice': string_object.string
    }

    return message



