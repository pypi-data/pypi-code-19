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

	def info_log(self, transaction_id, entity_id, profile_id, description):
		message = self.logger.info(transaction_id, entity_id, profile_id, description.replace('\n', ' '))
		self.publish_log_message(message)

	def error_log(self, transaction_id, entity_id, profile_id, description):
		message = self.logger.error(transaction_id, entity_id, profile_id, description.replace('\n', ' '))
		self.publish_log_message(message)

	def publish_message(self, routing_key, **kargs):
		self.rabbit_client.message_publisher_factory(routing_key, kargs)

	def publish_log_message(self, message):
		self.rabbit_client.message_publisher_factory('log', log=message)

	def publish_signup_message(self, type_account, type_user, profile_object, entity_object, user_object):
		user_account_object = queue_objs.UserAccountObject(type_account=type_account, type_user=type_user)

		message = self.rabbit_client.message_publisher_factory('signup', account=user_account_object, 
			profile=profile_object, entity=entity_object, user=user_object)

		return message

	def publish_upload_document_message(self, email, entity_name, document_name, link):
		entity_object = queue_objs.EntityObject(email=email, first_name=entity_name)
		document_object = queue_objs.DocumentObject(object_type=document_name, link=link)

		message = self.rabbit_client.message_publisher_factory('uploadDocument', entity=entity_object, 
			document=document_object)

		return message

