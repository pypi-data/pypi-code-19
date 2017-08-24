from mesfix import queue
from mesfix import mslog
from mesfix import queue_objs


class Helper(object):
    def __init__(self, microservice, rabbit_user, rabbit_password, rabbit_host,
                 rabbit_exchange, rabbit_type, endpoints):
        self.rabbit_client = queue.MesfixRabbitMQConnector(rabbit_user, rabbit_password,
                                                           rabbit_host, rabbit_exchange, rabbit_type)

        self.endpoints = endpoints
        self.logger = mslog.LogMessage(microservice)

    def publish_log_message(self, message):
        self.rabbit_client.message_publisher_factory('log', log=message)

    def info_log(self, transaction_id, entity_id, profile_id, description):
        description = description.replace('\n', ' ')
        message = self.logger.info(transaction_id, entity_id, profile_id, description)
        self.publish_log_message(message)

    def error_log(self, transaction_id, entity_id, profile_id, description):
        description = description.replace('\n', ' ')
        message = self.logger.error(transaction_id, entity_id, profile_id, description)
        self.publish_log_message(message)

    def publish_accept_contracts_mail(self, email):
        entity_object = queue_objs.EntityObject(email=email)

        message = self.rabbit_client.message_publisher_factory('acceptContracts',
                                                               entity=entity_object)

        return message

    def publish_validate_documents_mail(self, email):
        entity_object = queue_objs.EntityObject(email=email)

        message = self.rabbit_client.message_publisher_factory('validateDocuments',
                                                               entity=entity_object)

        return message

    def publish_upload_document_mail(self, email, first_name, last_name, type_user, document_type,
                                     document_number, link):
        entity_object = queue_objs.EntityObject(email=email, first_name=first_name,
                                                last_name=last_name, user_type=type_user)
        document_object = queue_objs.DocumentObject(object_type=document_type, object_id=document_number, link=link)

        message = self.rabbit_client.message_publisher_factory('uploadDocument',
                                                               entity=entity_object,
                                                               document=document_object)

        return message

    def publish_access_update_mail(self, type_account, type_user, email, first_name, last_name, company_name):
        user_account = queue_objs.UserAccountObject(type_account=type_account, type_user=type_user)
        entity_object = queue_objs.EntityObject(email=email, first_name=first_name, last_name=last_name)
        company_object = queue_objs.CompanyObject(name=company_name)

        message = self.rabbit_client.message_publisher_factory('access-update',
                                                               account=user_account,
                                                               entity=entity_object,
                                                               company=company_object)

        return message

    def publish_confirmed_payment_seller_mail(self, type_account, type_user, email, first_name, last_name,
                                       company_name, auction_id, value, due_date):
        user_account = queue_objs.UserAccountObject(type_account=type_account, type_user=type_user)
        entity_object = queue_objs.EntityObject(email=email, first_name=first_name, last_name=last_name)
        company_object = queue_objs.CompanyObject(name=company_name)
        transaction_object = queue_objs.AuctionTransactionObject(value=value)
        auction_object = queue_objs.AuctionObject(object_id=auction_id, auction_transaction_object=transaction_object,
                                                  due_date=due_date)

        message = self.rabbit_client.message_publisher_factory('confirmed-payment-seller',
                                                               account=user_account,
                                                               entity=entity_object,
                                                               company=company_object,
                                                               auction=auction_object)

        return message

    def publish_confirmed_payment_mail(self, type_account, type_user, email, first_name, last_name,
                                       company_name, auction_id):
        user_account = queue_objs.UserAccountObject(type_account=type_account, type_user=type_user)
        entity_object = queue_objs.EntityObject(email=email, first_name=first_name, last_name=last_name)
        company_object = queue_objs.CompanyObject(name=company_name)
        auction_object = queue_objs.AuctionObject(object_id=auction_id)

        message = self.rabbit_client.message_publisher_factory('confirmed-payment',
                                                               account=user_account,
                                                               entity=entity_object,
                                                               company=company_object,
                                                               auction=auction_object)

        return message

    def publish_update_bid_mail(self, type_account, type_user, email, first_name, last_name,
                                company_name, auction_id, value, annual_yield, link):
        user_account = queue_objs.UserAccountObject(type_account=type_account, type_user=type_user)
        entity_object = queue_objs.EntityObject(email=email, first_name=first_name, last_name=last_name)
        company_object = queue_objs.CompanyObject(name=company_name)
        transaction_object = queue_objs.AuctionTransactionObject(value=value)
        auction_object = queue_objs.AuctionObject(object_id=auction_id, auction_transaction_object=transaction_object,
                                                  annual_yield=annual_yield)
        link_object = queue_objs.LinkObject(link=link)

        message = self.rabbit_client.message_publisher_factory('update-bid',
                                                               account=user_account,
                                                               entity=entity_object,
                                                               company=company_object,
                                                               auction=auction_object,
                                                               link=link_object)

        return message

    def publish_auction_bid_mail(self, type_account, type_user, bid_number,
                                 net_value, value, due_date, payment_date, invoices, acceptor, seller,
                                 email, first_name, last_name, company_name, auction_number, annual_yield):
        user_account = queue_objs.UserAccountObject(type_account=type_account, type_user=type_user)
        offer_object = queue_objs.OfferObject(offer_id=bid_number,
                                              net_value=net_value, offered_value=value, due_date=due_date,
                                              payment_date=payment_date, profitability=annual_yield)
        document_objects = [queue_objs.DocumentObject(name=invoice) for invoice in invoices]
        acceptor = queue_objs.StringObject(acceptor)
        seller = queue_objs.StringObject(seller)
        entity_object = queue_objs.EntityObject(email=email, first_name=first_name, last_name=last_name)
        company_object = queue_objs.CompanyObject(name=company_name)
        auction_object = queue_objs.AuctionObject(object_id=auction_number)

        message = self.rabbit_client.message_publisher_factory('auction-bid',
                                                                 account=user_account,
                                                                 offer=offer_object,
                                                                 documents=document_objects,
                                                                 acceptor=acceptor,
                                                                 seller=seller,
                                                                 investor=entity_object,
                                                                 company=company_object,
                                                                 auction=auction_object)

        return message

    def publish_investment_certificate_mail(self, type_account, type_user, email, first_name,
                                                last_name, company_name, notice_message, link):
        user_account = queue_objs.UserAccountObject(type_account=type_account, type_user=type_user)
        entity_object = queue_objs.EntityObject(email=email, first_name=first_name, last_name=last_name)
        company_object = queue_objs.CompanyObject(name=company_name)
        notice = queue_objs.StringObject(string=notice_message)
        link = queue_objs.LinkObject(link=link)

        message = self.rabbit_client.message_publisher_factory('investment-certificate',
                                                                 account=user_account,
                                                                 entity=entity_object,
                                                                 company=company_object,
                                                                 link=link,
                                                                 string=notice)

        return message

    def publish_end_auction_mail(self, type_account, type_user, email, first_name,
                                 last_name, company_name, offer_id, net_value, offered_value,
                                 due_date, payment_date, rent_neta, acceptor, seller, documents, link):
        user_account = queue_objs.UserAccountObject(type_account=type_account, type_user=type_user)
        investor_object = queue_objs.EntityObject(email=email, first_name=first_name, last_name=last_name)
        company_object = queue_objs.CompanyObject(name=company_name)
        offer_object = queue_objs.OfferObject(offer_id=offer_id, net_value=net_value, offered_value=offered_value,
                                              due_date=due_date, payment_date=payment_date, profitability=rent_neta)
        document_objects = [queue_objs.DocumentObject(name=invoice) for invoice in documents]
        link = queue_objs.LinkObject(link=link)
        acceptor = queue_objs.StringObject(acceptor)
        seller = queue_objs.StringObject(seller)

        message = self.rabbit_client.message_publisher_factory('end-auction',
                                                                 account=user_account,
                                                                 investor=investor_object,
                                                                 company=company_object,
                                                                 offer=offer_object,
                                                                 acceptor=acceptor,
                                                                 seller=seller,
                                                                 documents=document_objects,
                                                                 link=link)

        return message

    def publish_transaction_received_mail(self, type_account, type_user, email, first_name, last_name,
                                company_name, auction_id, value):
        user_account = queue_objs.UserAccountObject(type_account=type_account, type_user=type_user)
        entity_object = queue_objs.EntityObject(email=email, first_name=first_name, last_name=last_name)
        company_object = queue_objs.CompanyObject(name=company_name)
        transaction_object = queue_objs.AuctionTransactionObject(value=value)
        auction_object = queue_objs.AuctionObject(object_id=auction_id, auction_transaction_object=transaction_object)

        message = self.rabbit_client.message_publisher_factory('transaction-received',
                                                               account=user_account,
                                                               entity=entity_object,
                                                               company=company_object,
                                                               auction=auction_object)

        return message
