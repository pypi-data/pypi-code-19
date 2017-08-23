# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import logging
import abc
import sys

if sys.version_info >= (3, 4):
    ABC = abc.ABC
else:
    ABC = abc.ABCMeta(str('ABC'), (), {})

import netmagus.form
import netmagus.session

logger = logging.getLogger(__name__)


class CancelButtonPressed(Exception):
    pass


class BackButtonPressed(Exception):
    pass


class ScreenBase(ABC):
    """
    Screen class represents a typical usage pattern for NetMagus form wizards.

    A Form is presented for user input, user data is entered, then data is
    validated.  If the data is invalid, show a pop-up HTML dialog and allow
    user to correct the entry.  Continue to loop until valid data is provided.
    If valid data received then transform response to correct data types, or
    store the input, or do additional workneeded for business logic and
    return.

    1 "next" button with provided name is displayed to execute data
    validation/return process. 1 "cancel" button is displayed to allow the
    user to exit on this screen.  Optionally present the user an additional
    "back" button to jump back to a previous Screen in the formula.

    This is an abstract base class and requires sublass implementations to obey
    the contract for the defined abstractmethods.  Subclasses may over-ride or
    call super() upon the concrete methods (such as __init__ and process_button)
    as desired.

    *** Example usage ***
    # self.session is set when NetMagusSession.display_ScreenBase() is called to
    # render a ScreenBase() in the UI
    class MinScreen(ScreenBase):
        def __init__(self):
            super(MinScreen, self).__init__()

        def generate_form(self):
            inputfield1 = form.TextInput(label='field1')
            return self.form = form.Form(name='Form1',
                                  description='Some Description',
                                  form=[inputfield1])

        def handle_back_button(self):
            # perform any clean up here
            pass

        def handle_cancel_button(self):
            # perform any clean up here
            cancel_form = form.Form(name='Cancelled',
                                    description='Operation Cancelled',
                                    form=[])
            return cancel_form

        def process_user_input(self):
            # perform any input transformation or work here
            pass

        def validate_user_input(self):
            # perform data validation here
            return True

        def return_error_message(self):
            # perform any work and then send error to the user when data invalid
            rpc.rpc_send(rpc.Html(title='Error', data='Data'))

        def return_screen_result(self):
            # perform any work and store the screen results if any
            self.session.session_data['data1'] = self.user_input['field1']

    """
    def __init__(self, session=None):
        """

        :param session: the NetMagusSession using this form
        :type session: netmagus.session.NetMagusSession
        """
        # the NetMagusSession that is using this screen
        self.session = session
        # the wellFormatedInput returned from the form
        self.user_input = None
        # flag to indicate that user input passed validation
        self.input_valid = False
        # used to track which button was pressed on the screen
        self.button_pressed = None
        # pointer to the next netmagus.screen.ScreenBase() instance to show
        self.next_screen = None
        # pointer to the netmagus.screen.ScreenBase() object if back is pressed
        self.back_screen = None

    @property
    def form(self):
        return self._render_form()

    def _render_form(self):
        """
        Calls the user's generate_form method and then does any desired clean
        up of the form attributes:

        * Auto-disables the back button if no back_screen is set

        :return:
        """
        user_form = self.generate_form()
        if not self.back_screen:
            user_form.disableBackButton = True
        return user_form

    def _process_user_input(self):
        """
        Used to track internally if the user overridden data validation
        function has passed and trigger formula to continue, reprompt for
        valid input, or error out

        """
        if self.validate_user_input():
            logger.debug('User input passed data validation')
            self.input_valid = True
            self.process_user_input()
        else:
            logger.debug('User input FAILED data validation')
            self.input_valid = False
            self.return_error_message()

    def process_button(self):
        """
        Provide default logic to handle the button pressed by the user
        on this screen.

        ex. - if button pressed was "cancel" execute formula clean-up logic;
        if button pressed was "back" go to previous screen; if button pressed
        was "next" validate and return data
        """
        logger.debug('UI button pressed: {}'.format(self.button_pressed))
        if self.button_pressed == 'cancel':
            raise CancelButtonPressed
        elif self.button_pressed == 'back':
            raise BackButtonPressed
        elif self.button_pressed.lower() == 'next':
            self._process_user_input()
        else:
            raise NotImplementedError('Handler for button {} not defined'
                                      .format(self.button_pressed))

    @abc.abstractmethod
    def validate_user_input(self):  # type: () -> bool
        """
        This method should be over-ridden by sublass with screen-specific
        logic to validate the value in self.user_input

        This method should simply indicate if the data entered by the user is
        adequate to proceed to call process_user_input and then proceed to
        display the next screen referenced in self.next_screen

        :return: True/False if data is Valid/Invalid
        """
        raise NotImplementedError

    @abc.abstractmethod
    def process_user_input(self):
        """
        Overide this method when subclassing to process any user input,
        store the results for access by other screens if necessary, and set
        any variable Screen.next_screen values to steer formula execution.

        Persistent data for a set of Screens should be stored in
        NetMagusSession.session_data (which is accessible to all Screen objects
        in the same session).  Or you may opt to store it in a global or other
        namespace objet usable by all Screens.

        This is used primarily in cases where formula may allow users to go
        back to previous screens or fork in different decision trees.  Screens
        at the end of a decision tree of screens may need to access prior screen
        data to perform operations upon the data from all or a subset of screens

        ex - read from self.user_input['IP Address'] and then generate an
        access-list entry in proper format and do
        self.screen_data='deny ip host 1.2.3.4 any' so that other screens can
        retrieve that ACL entry to be used in some other step of a process.

        Also, if this Screen may jump to a different screen depending upon
        user input, use this class method to set self.next_screen to the
        appropriate Screen instance dynamically.

        """
        return NotImplementedError

    @abc.abstractmethod
    def return_error_message(self):
        """
        Overide this method when sublcassing to send any desired HTML
        messages to the UI when user input data validation fails

        self.session.rpc_html instances can be sent via the
        self.session.rpc_send() method to appear in the HTML

        """
        raise NotImplementedError

    @abc.abstractmethod
    def handle_cancel_button(self):
        """
        Overide this method when sublcassing to take the desired actions when a
        user hits the cancel button during a formula execution step.

        This method should perform any required clean-up work and/or update any
        other forms that are displayed upon cancellation.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def handle_back_button(self):
        """
        Overide this method when subclassing to take desired action when a user
        presses the back button in a formula execution step.

        Use this method to perform any necessary clean-up work when going back
        to a previous screen.

        After this method is called by netmagus.session.display_ScreenBase(), it
        will then auto-display the screen referenced in self.back_screen

        """
        raise NotImplementedError

    @abc.abstractmethod
    def generate_form(self):  # type: () -> netmagus.form.Form
        """
        Overide this method when sublcassing to generate the desired NetMagus
        form to be seen in the UI.

        :return: the desired form with relevant form controls for user
        interaction
        :rtype: netmagus.form.Form
        """
        raise NotImplementedError