import sys
import queue
import queue_objs

link = 'https://medium.com/@sauvik_dolui/network-status-monitoring-on-ios-part-1-9a22276933dc'

entity_document_object = queue_objs.EntityDocumentObject('CC', '1010211109')
entity_object = queue_objs.EntityObject('2345345345', 'sc.valencia@mesfix.co',
                                        'Sebastian', 'Valencia', 'Seller', entity_document_object,
                                        'Diag 115A # 56B - 45', '3166259405')
user_account = queue_objs.UserAccountObject('43564356456', '10', 2)

company_document_object = queue_objs.EntityDocumentObject('NIT', '45435345-4')
company_object = queue_objs.CompanyObject('43543', 'sc.valencia@mesfix.co', 'EPISODIC',
                                          company_document_object, 'Diag 115A # 56B - 45', '3124234')

document_object = queue_objs.DocumentObject('234234', 'Mensual', link, 'Validacion 0')
document_object1 = queue_objs.DocumentObject('234235', 'Mensual', link, 'Validacion 1')
document_object2 = queue_objs.DocumentObject('234236', 'Mensual', link, 'Validacion 2')
document_object3 = queue_objs.DocumentObject('234237', 'Mensual', link, 'Validacion 3')
document_object4 = queue_objs.DocumentObject('234238', 'Mensual', link, 'Validacion 4')

auction_transaction_object = queue_objs.AuctionTransactionObject(45000)
auction_bid_object = queue_objs.AuctionBidObject(35000)
auction_object = queue_objs.AuctionObject('54645645', '2010-04-02 02:02:02', auction_transaction_object,
                                          auction_bid_object, 0.3)

link_object = queue_objs.LinkObject(link)
string_object = queue_objs.StringObject('This is a notice')

document_objects = [document_object1, document_object2, document_object3, document_object4]

offer_object = queue_objs.OfferObject('34554354', 450000, 3534554, '2010-04-02 02:02:02',
                                      '2010-02-11 02:02:02', 10)

connector = queue.MesfixRabbitMQConnector("mesfix-queue", "CtvuOHCFeDPtU9MC32k1",
                                          "localhost", "mesfix", "direct")


def test_accept_contracts():
    connector.message_publisher_factory('acceptContracts', account=user_account, entity=entity_object)


def test_validate_documents():
    connector.message_publisher_factory('validateDocuments', entity=entity_object)


def test_upload_documents():
    connector.message_publisher_factory('uploadDocument', entity=entity_object, document=document_object)


def test_ofac_user():
    connector.message_publisher_factory('ofacUser', entity=entity_object)


def test_service_error():
    message = 'requests.exceptions.ConnectionError: HTTPConnectionPool(host=u"219.231.143.96", port=18186)'
    procedure = 'callOFACScrapper'
    method = 'GET'
    code = '406'
    route = 'dev.mesfix.com/accept/ofac/86586686'
    logger_name = 'MESFIX_LOGGER_323'
    logger_level = 2

    error_object = queue_objs.ErrorObject(message, procedure, method, code, route, logger_name, logger_level)
    connector.message_publisher_factory('serviceError', error=error_object)


def test_missing_documents():
    connector.message_publisher_factory('missing-documents', account=user_account, entity=entity_object,
                                        company=company_object, documents=document_objects)


def test_access_update():
    connector.message_publisher_factory('access-update', account=user_account, entity=entity_object,
                                        company=company_object, link=link_object)


def test_confirmed_payment_seller():
    user_account = queue_objs.UserAccountObject('43564356456', '01', 2)
    connector.message_publisher_factory('confirmed-payment-seller', account=user_account, entity=entity_object,
                                        company=company_object, auction=auction_object)


def test_confirmed_payment():
    connector.message_publisher_factory('confirmed-payment', account=user_account, entity=entity_object,
                                        company=company_object, auction=auction_object)


def test_udate_bid():
    connector.message_publisher_factory('update-bid', account=user_account, entity=entity_object,
                                        company=company_object, auction=auction_object)


def test_auction_bid():
    acceptor, seller = queue_objs.StringObject("Margarita"), queue_objs.StringObject("Pedro")

    connector.message_publisher_factory('auction-bid', account=user_account, offer=offer_object,
                                        documents=document_objects, acceptor=acceptor, seller=seller,
                                        investor=entity_object,
                                        company=company_object, auction=auction_object)


def test_investment_certificate():
    connector.message_publisher_factory('investment-certificate', account=user_account, entity=entity_object,
                                        company=company_object, link=link_object, string=string_object)


def test_end_auction():
    connector.message_publisher_factory('end-auction', account=user_account, auction=auction_object,
                                        documents=document_objects, investor=entity_object, company=company_object,
                                        link=link_object,
                                        offer=offer_object)


def test_transaction_received():
    connector.message_publisher_factory('transaction-received', account=user_account, entity=entity_object,
                                        company=company_object, auction=auction_object)


def main():
    command = int(sys.argv[1])

    if command == 1:
        test_accept_contracts()
    elif command == 2:
        test_validate_documents()
    elif command == 3:
        test_upload_documents()
    elif command == 4:
        test_ofac_user()
    elif command == 5:
        test_service_error()
    elif command == 6:
        test_missing_documents()
    elif command == 7:
        test_access_update()
    elif command == 8:
        test_confirmed_payment_seller()
    elif command == 9:
        test_confirmed_payment()
    elif command == 10:
        test_udate_bid()
    elif command == 11:
        test_auction_bid()
    elif command == 12:
        test_investment_certificate()
    elif command == 13:
        test_end_auction()
    elif command == 14:
        test_transaction_received()


if __name__ == '__main__':
    main()
