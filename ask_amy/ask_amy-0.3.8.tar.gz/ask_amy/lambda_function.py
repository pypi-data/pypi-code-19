from __future__ import print_function

import logging
import sys
import json
from ask_amy.core.exceptions import ASKAmyError
from ask_amy.core.skill_factory import SkillFactory
from ask_amy.core.reply import Reply


logger = logging.getLogger()
logger.setLevel(logging.WARN)


def lambda_handler(event_dict, context):
    logger.warn("**************** entering NEW lambda_handler")
    try:

        dialog_obj = SkillFactory.build()
        response = dialog_obj.begin(event_dict)
    except ASKAmyError as error:
        logger.critical("ASK Amy failed with critical Error: {}".format(error))
        response_dict = {
            "speech_out_text": "Error while processing your request, Please try again. Good Bye.",
            "should_end_session": True}
        response = Reply.build(response_dict)

    return response


if __name__ == "__main__":
    with open(sys.argv[1], 'r') as file_ptr:
            event = json.load(file_ptr)

    reply = lambda_handler(event, None)
    print(reply)

# To test your function locally run the below in your project directory
# PYTHONPATH=./alexa_skill.zip python  ./dist/ask_amy/lambda_function.py ./event.json