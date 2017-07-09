'''
Managers.py
'''

import json
import requests
import validators

from .objects.base import Manager
from .objects.customers import Customer
from .objects.errors import APIConnectionFailedError, URLValidationError
from .objects.filters import Filter
from .objects.plans import Plan
from .objects.transfers import Transfer
from .objects.transactions import Transaction
from .objects.subaccounts import SubAccount

from .paystack_config import PaystackConfig
from .mixins import CreatableMixin, RetrieveableMixin, UpdateableMixin

class Utils(Manager):
    '''

    '''

    def __init__(self):
        super().__init__()


    def resolve_card_bin(self, card_bin, endpoint='/decision/bin/'):
        '''

        '''
        card_bin = card_bin[:6]
        url = self.PAYSTACK_URL + endpoint + card_bin
        headers, _ = self.build_request_args()

        response = requests.get(url, headers=headers)
        content = self.parse_response_content(response.content)

        status, message = self.get_content_status(content)
        if status:
            return content['data']
        
    def get_banks(self, endpoint='/bank'):
        '''

        '''
        url = self.PAYSTACK_URL + endpoint
        headers, _ = self.build_request_args()

        response = requests.get(url, headers=headers)
        content = self.parse_response_content(response.content)

        status, message = self.get_content_status(content)
        if status:
            return content['data']

    def resolve_bvn(self, bvn, endpoint='/bank/resolve_bvn/'):
        url = self.PAYSTACK_URL + endpoint + bvn
        headers, _ = self.build_request_args()

        response = requests.get(url, headers=headers)
        content = self.parse_response_content(response.content)

        status, message = self.get_content_status(content)
        if status:
            return content['data']
    
    def resolve_account_number(self, account_number, bank_code, endpoint='/bank/resolve'):
        '''
        '''        
        params = "?account_number=%s&bank_code=%s" % (account_number, bank_code)
        url = self.PAYSTACK_URL + endpoint + params

        headers, _ = self.build_request_args()

        response = requests.get(url, headers=headers)
        content = self.parse_response_content(response.content)

        status, message = self.get_content_status(content)
        if status:
            return content['data']
        


class TransactionsManager(RetrieveableMixin, Manager):
    '''
    TransactionsManager class that handles every part of a transaction

    Attributes:
    amount : Transaction cost
    email : Buyer's email
    reference
    authorization_url
    card_locale : Card location for application of paystack charges
    '''

    LOCAL_COST = PaystackConfig.LOCAL_COST
    INTL_COST = PaystackConfig.INTL_COST
    PASS_ON_TRANSACTION_COST = PaystackConfig.PASS_ON_TRANSACTION_COST

    __endpoint = '/transaction'
    __object_class = Transaction


    def __init__(self, endpoint='/transaction'):
        super().__init__()
        self.__endpoint = endpoint


    def initialize_transaction(self, method, transaction: Transaction,
                               callback_url='', endpoint='/initialize'):
        '''
        Initializes a paystack transaction.
        Returns an authorization url which points to a paystack form if the method is standard.
        Returns a dict containing transaction information if the method is inline or inline embed

        Arguments:
        method : Specifies whether to use paystack inline, standard or inline embed
        callback_url : URL paystack redirects to after a user enters their card details
        plan_code : Payment plan code
        endpoint : Paystack API endpoint for intializing transactions
        '''

        method = method.upper()
        if method not in ('STANDARD', 'INLINE', 'INLINE EMBED'):
            raise ValueError("method argument should be STANDARD, INLINE or INLINE EMBED")

        if self.PASS_ON_TRANSACTION_COST:
            transaction.amount = transaction.full_transaction_cost(transaction.card_locale,
                                                                   self.LOCAL_COST, self.INTL_COST)

        data = json.JSONDecoder().decode(transaction.to_json())

        if callback_url:
            if validators.url(callback_url):
                data['callback_url'] = callback_url

            else:
                raise URLValidationError

        if method in ('INLINE', 'INLINE EMBED'):
            data['key'] = PaystackConfig.PUBLIC_KEY
            return data

        headers, data = self.build_request_args(data)

        url = self.PAYSTACK_URL + self.__endpoint + endpoint
        response = requests.post(url, headers=headers, data=data)
        content = response.content
        content = self.parse_response_content(content)


        status, message = self.get_content_status(content)

        #status = True for a successful connection
        if status:
            data = json.dumps(content['data'])
            transaction = Transaction.from_json(data)
            return transaction
        else:
            #Connection failed
            raise APIConnectionFailedError(message)

    def verify_transaction(self, transaction: Transaction, endpoint='/verify/'):
        '''
        Verifies a payment using the transaction reference.

        Arguments:
        endpoint : Paystack API endpoint for verifying transactions
        '''

        endpoint += transaction.reference
        url = self.PAYSTACK_URL + self.__endpoint + endpoint

        headers, _ = self.build_request_args()
        response = requests.get(url, headers=headers)
        content = response.content
        content = self.parse_response_content(content)

        status, message = self.get_content_status(content)

        if status:
            data_dict = content['data']
            data = json.dumps(content['data'])
            transaction = Transaction.from_json(data)
            transaction.email = data_dict['customer']['email']
            transaction.authorization_code = data_dict['authorization']['authorization_code']
            return transaction
        else:
            raise APIConnectionFailedError(message)

    def charge_authorization(self, transaction: Transaction, endpoint='/charge_authorization'):
        data = transaction.to_json()
        headers, _ = self.build_request_args()

        response = requests.post(self.PAYSTACK_URL + self.__endpoint + endpoint,
                                 headers=headers, data=data)
        content = response.content
        content = self.parse_response_content(content)

        status, message = self.get_content_status(content)

        #status = True for a successful connection
        if status:
            return content['data']
        else:
            #Connection failed
            raise APIConnectionFailedError(message)

    def get_total_transactions(self):
        '''
        Get total amount recieved from transactions
        '''
        headers, _ = self.build_request_args()
        url = self.PAYSTACK_URL + self.__endpoint
        url += '/totals'
        response = requests.get(url, headers=headers)

        content = response.content
        content = self.parse_response_content(content)

        status, message = self.get_content_status(content)

        if status:
            return content['data']
        else:
            raise APIConnectionFailedError(message)

    # def get_transactions(self):
    #     '''
    #     Gets all transactions
    #     '''
    #     headers, _ = self.build_request_args()

    #     response = requests.get(self.PAYSTACK_URL + self.__endpoint, headers=headers)

    #     content = response.content
    #     content = self.parse_response_content(content)

    #     status, message = self.get_content_status(content)

    #     if status:
    #         data = content['data']
    #         for item in data:
    #             data_dict = item
    #             data = json.dumps(content['data'])
    #             transaction = Transaction.from_json(data)
    #             transaction.email = data_dict['customer']['email']
    #             if data_dict['authorization']:
    #                 transaction.authorization_code = data_dict['authorization']['authorization_code']
    #             return transaction
    #     else:
    #         raise APIConnectionFailedError(message)

    # def get_transaction(self, transaction_id):
    #     '''
    #     Gets transaction with the specified id
    #     '''
    #     headers, _ = self.build_request_args()

    #     url = self.PAYSTACK_URL + self.__endpoint
    #     url += '/%s' % (str(transaction_id))
    #     response = requests.get(url, headers=headers)

    #     content = response.content
    #     content = self.parse_response_content(content)

    #     status, message = self.get_content_status(content)

    #     if status:
    #         data_dict = content['data']
    #         data = json.dumps(data_dict)
    #         transaction = Transaction.from_json(data)
    #         transaction.email = data_dict['customer']['email']
    #         if data_dict['authorization']:
    #             transaction.authorization_code = data_dict['authorization']['authorization_code']
    #         return transaction

    #     else:
    #         raise APIConnectionFailedError(message)


    def filter_transactions(self, amount_range: range, transactions):
        '''
        Returns all transactions with amounts in the given amount_range
        '''
        results = []
        for transaction in transactions:
            if Filter.filter_amount(amount_range, transaction):
                results.append(transaction)

        return results

class CustomersManager(CreatableMixin, RetrieveableMixin, UpdateableMixin, Manager):
    '''
    CustomersManager class which handels actions for Paystack Customers

    Attributes :
    __endpoint : Paystack API endpoint for 'customers' actions

    '''
    __endpoint = '/customer'
    __object_class = Customer

    def __init__(self):
        super().__init__()

    # def create_customer(self, customer: Customer, meta=None):
    #     '''
    #     Method for creating a new customer.

    #     Arguments :
    #     email  : Customer's email address
    #     customer : Customer object
    #     meta : Dict which can contain additional customer information
    #     '''

    #     if not isinstance(customer, Customer):
    #         raise TypeError("customer argument should be an instance of the Customer class")

    #     if validators.email(customer.email):
    #         data = customer.to_json(pickled=False)

    #         headers, _ = self.build_request_args()

    #     else:
    #         raise InvalidEmailError


    #     response = requests.post(self.PAYSTACK_URL + self.__endpoint, headers=headers, data=data)

    #     content = response.content
    #     content = self.parse_response_content(content)

    #     status, message = self.get_content_status(content)

    #     if status:
    #         if message == 'Customer created':
    #             return content['data']
    #         else:
    #             raise ValueError("A customer with this email already exists")

    #     else:
    #         raise APIConnectionFailedError(message)


    # def get_customers(self):
    #     '''
    #     Method which returns all registered customers
    #     '''
    #     headers, _ = self.build_request_args()

    #     response = requests.get(self.PAYSTACK_URL + self.__endpoint, headers=headers)

    #     content = response.content
    #     content = self.parse_response_content(content)

    #     status, message = self.get_content_status(content)

    #     if status:
    #         data = content['data']
    #         meta = content['meta']
    #         customers = []
    #         for item in data:
    #             item = json.dumps(item)
    #             customer = Customer.from_json(item)
    #             customers.append(customer)
    #         return (customers, meta)

    #     else:
    #         raise APIConnectionFailedError(message)


    # def get_customer(self, customer_id):
    #     '''
    #     Method for getting a particular customer with the specified customer_id

    #     Arguments :
    #     customer_id : Customer id

    #     '''
    #     headers, _ = self.build_request_args()
    #     url = "%s%s/%s" % (self.PAYSTACK_URL, self.__endpoint, customer_id)
    #     response = requests.get(url, headers=headers)

    #     content = response.content
    #     content = self.parse_response_content(content)

    #     status, message = self.get_content_status(content)

    #     if status:
    #         data = json.dumps(content['data'])
    #         customer = Customer.from_json(data)
    #         return customer
    #     else:
    #         raise APIConnectionFailedError(message)

    # def update_customer(self, customer_id, updated_customer: Customer):
    #     '''
    #     Method for updating an existing customer

    #     Arguments :
    #     id : Customer id
    #     data : Dict which contains the values to be updated as keys
    #             and the updated information as the values
    #     '''
    #     if not isinstance(updated_customer, Customer):
    #         raise TypeError("customer argument should be of type 'Customer' ")

    #     data = updated_customer.to_json(pickled=False)
    #     headers, _ = self.build_request_args()
    #     url = "%s%s/%s" % (self.PAYSTACK_URL, self.__endpoint, customer_id)

    #     response = requests.put(url, headers=headers, data=data)
    #     content = response.content
    #     content = self.parse_response_content(content)

    #     status, message = self.get_content_status(content)
    #     if status:
    #         data = json.dumps(content['data'])
    #         return Customer.from_json(data)
    #     else:
    #         raise APIConnectionFailedError(message)

    def set_risk_action(self, risk_action, customer: Customer):
        '''
        Method for either blacklisting or whitelisting a customer

        Arguments :
        risk_action : (allow or deny)
        customer_id : Customer id

        '''

        if not isinstance(customer, Customer):
            raise TypeError("customer argument should be of type 'Customer' ")

        endpoint = '/set_risk_action'

        if risk_action not in ('allow', 'deny'):
            raise ValueError("Invalid risk action")

        else:
            data = {'customer' : customer.id, 'risk_action' : risk_action}
            headers, data = self.build_request_args(data)
            url = "%s%s" % (self.PAYSTACK_URL + self.__endpoint, endpoint)

            response = requests.post(url, headers=headers, data=data)

            content = response.content
            content = self.parse_response_content(content)

            status, message = self.get_content_status(content)

            if status:
                data = json.dumps(content['data'])
                return Customer.from_json(data)
            else:
                raise APIConnectionFailedError(message)

    def deactive_authorization(self, authorization_code):
        '''
        Method to deactivate an existing authorization

        Arguments :
        authorization_code : Code for the transaction to be deactivated

        '''
        data = {'authorization_code' : authorization_code}
        headers, data = self.build_request_args(data)

        url = "%s/deactivate_authorization" % (self.PAYSTACK_URL + self.__endpoint)
        response = requests.post(url, headers=headers, data=data)

        content = response.content
        content = self.parse_response_content(content)

        status, message = self.get_content_status(content)

        if status:
            return content['data']
        else:
            raise APIConnectionFailedError(message)




class PlanManager(CreatableMixin, RetrieveableMixin, UpdateableMixin, Manager):
    '''
    Plan Manager class
    '''

    __endpoint = '/plan'
    __object_class = Plan

    def __init__(self, endpoint='/plan'):
        super().__init__()
        self.__endpoint = endpoint

    # def create_plan(self, plan: Plan):
    #     '''
    #     Method for creating plans

    #     Arguments:
    #     plan : Plan object

    #     '''
    #     url = self.PAYSTACK_URL + self.__endpoint

    #     data = plan.to_json()

    #     headers, data = self.build_request_args(data)

    #     response = requests.post(url, headers=headers, data=data)
    #     content = response.content
    #     content = self.parse_response_content(content)

    #     status, message = self.get_content_status(content)

    #     if status:
    #         data = json.dumps(content['data'])
    #         return Plan.from_json(data)
    #     else:
    #         raise APIConnectionFailedError(message)

    # def get_plans(self):
    #     '''
    #     Method for getting plans
    #     '''
    #     headers, _ = self.build_request_args()
    #     response = requests.get(self.PAYSTACK_URL + self.__endpoint, headers=headers)

    #     content = response.content
    #     content = self.parse_response_content(content)

    #     status, message = self.get_content_status(content)

    #     if status:
    #         data = content['data']
    #         meta = content['meta']
    #         plans = []
    #         for item in data:
    #             item = json.dumps(item)
    #             plan = Plan.from_json(item)
    #             plans.append(plan)
    #             return (plans, meta)
    #     else:
    #         raise APIConnectionFailedError(message)

    # def get_plan(self, plan_id):
    #     '''
    #     Method for getting a plan with the specified id
    #     '''
    #     headers, _ = self.build_request_args()

    #     url = "%s%s/%s" % (self.PAYSTACK_URL, self.__endpoint, plan_id)
    #     response = requests.get(url, headers=headers)

    #     content = response.content
    #     content = self.parse_response_content(content)

    #     status, message = self.get_content_status(content)

    #     if status:
    #         data = json.dumps(content['data'])
    #         plan = Plan.from_json(data)
    #         return plan
    #     else:
    #         raise APIConnectionFailedError(message)

    # def update_plan(self, plan_id, updated_plan: Plan):
    #     '''
    #     Method for updating existing plan
    #     '''
    #     if not isinstance(updated_plan, Plan):
    #         raise TypeError("updated_plan argument should be of type 'Plan' ")

    #     data = updated_plan.to_json()
    #     headers, _ = self.build_request_args()
    #     url = "%s%s/%s" % (self.PAYSTACK_URL, self.__endpoint, plan_id)

    #     response = requests.put(url, headers=headers, data=data)
    #     content = response.content
    #     content = self.parse_response_content(content)

    #     status, message = self.get_content_status(content)
    #     if status:
    #         data = json.dumps(content['data'])
    #         return Plan.from_json(data)
    #     else:
    #         raise APIConnectionFailedError(message)



class TransfersManager(CreatableMixin, RetrieveableMixin, UpdateableMixin, Manager):
    '''
    TransfersManager class
    '''

    __endpoint = '/transfer'
    __object_class = Transfer

    def __init__(self, endpoint='/transfer'):
        super().__init__()
        self.__endpoint = endpoint


    # def initiate_transfer(self, transfer: Transfer):
    #     '''
    #     Method to start a transfer to a bank account.
    #     '''

    #     data = transfer.to_json()


    #     headers, _ = self.build_request_args()

    #     url = self.PAYSTACK_URL + self.__endpoint
    #     response = requests.post(url, headers=headers, data=data)
    #     content = response.content
    #     content = self.parse_response_content(content)


    #     status, message = self.get_content_status(content)

    #     if status:
    #         data = json.dumps(content['data'])
    #         transfer = Transfer.from_json(data)
    #         return transfer

    #     else:
    #         #Connection failed
    #         raise APIConnectionFailedError(message)


    # def get_transfers(self):
    #     '''
    #     Method to get all paystack transfers
    #     '''
    #     headers, _ = self.build_request_args()

    #     url = self.PAYSTACK_URL + self.__endpoint
    #     response = requests.get(url, headers=headers)
    #     content = response.content
    #     content = self.parse_response_content(content)

    #     status, message = self.get_content_status(content)

    #     if status:
    #         data = content['data']
    #         transfers = []
    #         for item in data:
    #             item = json.dumps(item)
    #             transfers.append(Transfer.from_json(item))

    #         return transfers

    #     else:
    #         #Connection failed
    #         raise APIConnectionFailedError(message)

    # def get_transfer(self, transfer_id):
    #     '''
    #     Method to get paystack transfer with the specified id
    #     '''
    #     headers, data = self.build_request_args()

    #     url = self.PAYSTACK_URL + self.__endpoint
    #     url += '/%s' % (transfer_id)
    #     response = requests.post(url, headers=headers)
    #     content = response.content
    #     content = self.parse_response_content(content)

    #     status, message = self.get_content_status(content)

    #     if status:
    #         data = json.dumps(content['data'])
    #         return Transfer.from_json(data)
    #     else:
    #         #Connection failed
    #         raise APIConnectionFailedError(message)

    def finalize_transfer(self, transfer_id, otp):
        '''
        Method for finalizing transfers
        '''
        transfer_id = str(transfer_id)
        otp = str(otp)

        data = {'transfer_code' : transfer_id, 'otp' : otp}
        headers, data = self.build_request_args(data)

        url = self.PAYSTACK_URL + self.__endpoint
        url += '/finalize_transfer'
        response = requests.post(url, headers=headers, data=data)
        content = response.content
        content = self.parse_response_content(content)


        status, message = self.get_content_status(content)

        if status:
            data = content['data']
            return data

        else:
            #Connection failed
            raise APIConnectionFailedError(message)




class SubAccountManager(CreatableMixin, RetrieveableMixin, UpdateableMixin, Manager):
    '''

    '''
    __endpoint = None
    __object_class = SubAccount

    def __init__(self, endpoint='/subaccount'):
        super().__init__()
        self.__endpoint = endpoint

    # def create_sub_account(self, sub_account: SubAccount):
    #     url = self.PAYSTACK_URL + self.__endpoint

    #     data = sub_account.to_json()

    #     headers, data = self.build_request_args(data)

    #     response = requests.post(url, headers=headers, data=data)
    #     content = response.content
    #     content = self.parse_response_content(content)

    #     status, message = self.get_content_status(content)

    #     if status:
    #         data = json.dumps(content['data'])
    #         return SubAccount.from_json(data)
    #     else:
    #         raise APIConnectionFailedError(message)

    # def get_sub_accounts(self):
    #     '''

    #     '''
    #     headers, _ = self.build_request_args()
    #     response = requests.get(self.PAYSTACK_URL + self.__endpoint, headers=headers)

    #     content = response.content
    #     content = self.parse_response_content(content)

    #     status, message = self.get_content_status(content)

    #     if status:
    #         data = content['data']
    #         meta = content['meta']
    #         plans = []
    #         for item in data:
    #             item = json.dumps(item)
    #             plan = Plan.from_json(item)
    #             plans.append(plan)
    #             return (plans, meta)
    #     else:
    #         raise APIConnectionFailedError(message)
