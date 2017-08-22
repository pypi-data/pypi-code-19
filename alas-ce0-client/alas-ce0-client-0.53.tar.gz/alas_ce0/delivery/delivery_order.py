from enum import Enum

from alas_ce0.common.client_base import EntityClientBase
from alas_ce0.management.task import TaskClient


class DeliveryOrderProcessType(Enum):
    B2bDelivery = 1
    B2bReception = 2
    Packaging = 3
    CarrierDispatch = 4
    CarrierDelivery = 5
    SerReception = 6
    VehicleLoad = 7
    B2cDelivery = 8


class DeliveryOrderStakeholderType(Enum):
    Sender = 1
    Receiver = 2
    ReceiverEmployee = 3
    PackagerEmployee = 4
    DispatcherEmployee = 5
    IntermediateCarrier = 6
    RegionalPartner = 7
    ControllerEmployee = 8
    MessengerEmployee = 9
    DeliveryManager = 10


class DeliveryOrderStatusType(Enum):
    Planning = 1
    PlanningChanged = 2
    PlanningApproved = 3
    VirtuallyReceived = 4
    PhisicallyReceived = 5
    B2BReceptionRejected = 6
    Packaging = 7
    TIReceptionWaiting = 8
    SERTravelling = 9
    SERReceived = 10
    ReplacementWaiting = 11
    DeliveryScheduled = 12
    B2CTraveling = 13
    Delivered = 14
    PackagingIssueReturned = 15
    ODFReturned = 16
    ODSFReturned = 17
    Pending = 18
    PrioritizedPending = 19
    NonDeliverable = 20
    B2BReturning = 21
    B2BReturned = 22


class DeliveryOrderRequestClient(EntityClientBase):
    entity_endpoint_base_url = '/delivery/delivery-order-requests/'

    def __init__(self, country_code='cl', **kwargs):
        super(DeliveryOrderRequestClient, self).__init__(**kwargs)
        self.entity_endpoint_base_url += country_code + '/'


class DeliveryOrderClient(EntityClientBase):
    entity_endpoint_base_url = '/delivery/delivery-orders/'

    def __init__(self, country_code='cl', **kwargs):
        super(DeliveryOrderClient, self).__init__(**kwargs)
        self.entity_endpoint_base_url += country_code + '/'

    def create_from_request(self, delivery_order_request_id, async=True):
        params = {
            'delivery_order_request_id': delivery_order_request_id
        }

        if async:
            return TaskClient(**self.args).enqueue('delivery-order-create', params)
        else:
            return self.http_post_json(self.entity_endpoint_base_url + "_create-from-request", params)

    def get_agenda(self, date_from, date_to, process_types, stakeholder_types=None):
        param = {
            'date_from': date_from,
            'date_to': date_to,
            'process_types': process_types,
            'stakeholder_types': stakeholder_types
        }

        return self.http_post_json(self.entity_endpoint_base_url + "_agenda", param)

    def change_status(self, id, params):
        return self.http_post_json(self.entity_endpoint_base_url + "{0}/_change-status".format(id), params)

    def change_planning(self, id, params):
        return self.http_post_json(self.entity_endpoint_base_url + "{0}/_change-planning".format(id), params)

    def upload_file(self, user_name, sender_code, base64_content, file_format="txt"):
        params = {
            'user_name': user_name,
            'sender_code': sender_code,
            'base64_content': base64_content,
            'format': file_format,
        }
        return self.http_post_json(self.entity_endpoint_base_url + "_upload-file", params)

    def validate_customer(self, id, params):
        return self.http_post_json(self.entity_endpoint_base_url + "{0}/_validate-customer".format(id), params)
