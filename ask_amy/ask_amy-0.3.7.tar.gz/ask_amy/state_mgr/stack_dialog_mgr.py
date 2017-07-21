from ask_amy.core.default_dialog import DefaultDialog
from ask_amy.core.request import IntentRequest
from ask_amy.core.reply import Reply
from ask_amy.utilities.iso_8601_type import ISO8601_Validator
from ask_amy.utilities.custom_type import Custom_Validator
from ask_amy.core.exceptions import CustomTypeLoadError
from functools import wraps
import logging

logger = logging.getLogger()

class StackDialogManager(DefaultDialog):



    def requested_value_intent(self):
        """
        This intent is expected to be called when we need to capture a bit of info the we may have failed
        to capture on a one shot.
        :return:
        """
        logger.debug('**************** entering StackDialogManager.requested_value_intent')

        established_dialog = self.peek_established_dialog()
        if established_dialog != self.intent_name:
            # we should not come here unless directed by another intent
            return self.handle_session_end_confused()
        else:
            self.pop_established_dialog()
            established_dialog = self.peek_established_dialog()
            self._intent_name = established_dialog
            return self.execute_method(established_dialog)


    def redirect_to_initialize_dialog(self,intent_name):
        """
        Simple redirect. We use this if an intent is called but a prior intent was expected
        :param intent_name:
        :return:
        """
        self._intent_name = intent_name
        return self.execute_method(intent_name)


    def get_expected_intent_for_data(self, data_name):
        return self.get_value_from_dict(['slots', data_name, 'expected_intent'])

    def handle_session_end_confused(self):
        """
        Called if we are in an intent but don't have the info to move forward
        and are not sure how or why alex called us here (obviously this should not
        be a common occurrence.)
        :return:
        """
        logger.debug('**************** entering StackDialogManager.handle_session_end_confused')
        # can we re_prompt?
        dialog_state = self.peek_established_dialog()
        if 'retry_attempted' not in dialog_state.keys():
            prompt_dict = {"speech_out_text": "Could you please repeat or say help.",
                           "should_end_session": False}

            if 'slot_name' in dialog_state.keys():
                requested_value_nm = dialog_state['slot_name']
                prompt_dict = self.get_re_prompt_for_slot_data(requested_value_nm)

            dialog_state['retry_attempted'] = True
            return Reply.build(prompt_dict, self.event)
        else:
            # we are done
            self._intent_name = 'handle_session_end_confused'
            return self.handle_default_intent()

    def get_re_prompt_for_slot_data(self, data_name):
        slot_data_details = self.get_value_from_dict(['slots', data_name])
        if 're_prompt_text' in slot_data_details:
            slot_data_details['speech_out_text'] = slot_data_details['re_prompt_text']
            del slot_data_details['re_prompt_text']
        if 're_prompt_ssml' in slot_data_details:
            slot_data_details['speech_out_text'] = slot_data_details['re_prompt_ssml']
            del slot_data_details['re_prompt_ssml']
        slot_data_details['should_end_session'] = False
        return slot_data_details

    def is_good_state(self):
        """
        Checks the state of the dialog and establish a conversation if this is the first
        interaction on a multi step intent
        :return:
        """
        logger.debug('**************** entering StackDialogManager.is_good_state')
        # did the expected intent get called?
        state_good = True
        established_dialog = self.peek_established_dialog()
        if established_dialog is not None:
            if established_dialog['intent_name'] != self.intent_name:
                state_good = False
        else:
            self.push_established_dialog(self.intent_name)
        return state_good

    def peek_established_dialog(self):
        """
        peek at the current intent state
        :return:
        """
        logger.debug("**************** entering StackDialogManager.peek_established_dialog")
        intent_attributes = None
        if self.session.attribute_exists('established_dialog'):
            dialog_stack = self.session.attributes['established_dialog']
            if len(dialog_stack) > 0:
                intent_attributes = dialog_stack[len(dialog_stack) - 1]
        return intent_attributes

    def push_established_dialog(self, intent_name):
        """
        Push an intent and its state  onto the stack
        :param intent_name:
        :return:
        """
        logger.debug("**************** entering Dialog.push_established_dialog")
        new_intent_attributes={"intent_name": intent_name}
        # If we dont have an established_dialog create one
        if 'established_dialog' not in self.session.attributes.keys():
            self.session.attributes['established_dialog'] = [new_intent_attributes]
            return

        dialog_stack = self.session.attributes['established_dialog']

        # if we do have an established_dialog but no active intent_attributes add the new one
        active_intent_attributes = self.peek_established_dialog()
        if active_intent_attributes is None:
            dialog_stack.append(new_intent_attributes)
        else:
            # if we do have an established_dialog and intent_attributes
            # is the new intent different from the one I am working on?
            # if so add it otherwise just use the one that is established
            if active_intent_attributes['intent_name'] != intent_name:
                dialog_stack.append(new_intent_attributes)

    def pop_established_dialog(self):
        """
        pop an intent state from the stack
        :return:
        """
        logger.debug("**************** entering StackDialogManager.pop_established_dialog")
        intent_attributes = None
        if self.session.attribute_exists('established_dialog'):
            dialog_stack = self.session.attributes['established_dialog']
            intent_attributes = dialog_stack.pop()
        return intent_attributes

    def reset_established_dialog(self):
        """
        reset the whole intent dialog stack
        :return:
        """
        logger.debug("**************** entering StackDialogManager.reset_established_dialog")
        if self.session.attribute_exists('established_dialog'):
            dialog_stack = self.session.attributes['established_dialog']
            del dialog_stack[:]

    def required_fields_process(self, required_fields):
        """
        review the required fields to process this intent if we have all the data move forward
        if not create a reply that will call an appropriate intent to get the missing data
        :param required_fields:
        :return:
        """
        reply_dict = None
        intent_attributes = self.peek_established_dialog()
        for key in required_fields:
            if key not in intent_attributes.keys():
                expected_intent = self.get_expected_intent_for_data(key)
                self.push_established_dialog(expected_intent)
                intent_attributes['slot_name'] = key
                reply_slot_dict = self.get_slot_data_details(key)
                return Reply.build(reply_slot_dict, self.event)

        return reply_dict

    def get_slot_data_details(self, data_name):
        slot_data_details = self.get_value_from_dict(['slots', data_name])
        slot_data_details['should_end_session'] = False
        return slot_data_details

    def slot_data_to_intent_attributes(self):
        """
        Move slot data into intent state data. This will collect the data required to
        execute the initial intent. (i.e. similar to flow state in JSF)
        :return:
        """
        logger.debug("**************** entering StackDialogManager.slot_data_to_intent_attributes")
        # If we have an Intent Request map the slot values to the session
        if isinstance(self.event.request, IntentRequest):
            slots_dict = self.event.request.slots
            intent_attributes = self.peek_established_dialog()
            for name in slots_dict.keys():
                # get the value for this name if available
                value = self.request.value_for_slot_name(name)
                if value is not None:
                    # If this is a 'requested_value' do we have a field to map to?
                    if name == 'requested_value':
                        if 'slot_name' in intent_attributes.keys():
                            name = intent_attributes['slot_name']
                    intent_attributes[name] = value

    def required_fields_in_session_attributes_to_intent_attributes(self, required_fields):
        """
        Move session data into intent state data. This will stage the data we have already collected
        that is required to execute the intent.
        :return:
        """
        logger.debug("**************** entering StackDialogManager.required_fields_in_session_attributes_to_intent_attributes")
        # If we have an Intent Request map the slot values to the session
        if isinstance(self.event.request, IntentRequest):
            intent_attributes = self.peek_established_dialog()
            for name in required_fields:
                if self.session.attribute_exists(name):
                    intent_attributes[name] = self.session.attributes[name]


    def intent_attributes_to_request_attributes(self):
        dialog_state = self.peek_established_dialog()
        for key in dialog_state.keys():
            self.request.attributes[key]= dialog_state[key]

    def validate_slot_data_type(self, name, value):
        """
        Delegates to the appropriate validator if a type check is defined in the dialog_dict
        :param name:
        :param value:
        :return:
        """
        logger.debug("**************** entering StackDialogManager.validate_slot_data_type")
        slot_type = self.get_value_from_dict(['slots', name, 'type'])
        valid = True
        if slot_type is None:
            return valid # If type is not defined skip validation test
        else:
            if slot_type.startswith('AMAZON.'):
                valid = ISO8601_Validator.is_valid_value(value, slot_type)
            else:
                try:
                    validator = Custom_Validator.class_from_str(slot_type)
                    valid = validator.is_valid_value(value)
                except CustomTypeLoadError:
                    logger.debug("Unable to load {}".format(slot_type))
                    valid = True

        return valid


def required_fields(fields):
    """
    Required fields decorator manages the state of the intent
    :param fields:
    :return:
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            obj = args[0]
            if isinstance(obj,StackDialogManager):
                if obj.is_good_state():
                    obj.required_fields_in_session_attributes_to_intent_attributes(fields)
                    obj.slot_data_to_intent_attributes()
                    need_additional_data = obj.required_fields_process(fields)
                    if need_additional_data is not None:
                        return need_additional_data
                else:
                    return obj.handle_session_end_confused()

                obj.intent_attributes_to_request_attributes()
                ret_val = func(*args, **kwargs)
                obj.pop_established_dialog()
            else:
                ret_val = func(*args, **kwargs)
            return ret_val
        return wrapper
    return decorator
