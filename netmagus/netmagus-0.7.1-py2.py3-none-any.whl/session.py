# coding=utf-8
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import importlib
import json
import logging
import os
import pickle
import traceback

import netmagus.form
import netmagus.rpc
import netmagus.screen


class NetMagusSession(object):
    """
    This class is a wrapper to handle an interactive session between the
    NetMagus backend and a user script.  It serves as a unifed API for user
    script operations to send/receive data with the NetMagus backend.  It
    also serves as a unified API for the NetMagus backend to call and execute
    user scripts.

    The NetMagus backend will call the module as (ex.):
        "python -m netmagus --script user.py --token aBcDeF --input-file
        /some/path/to/aBcDeF.json --loglevel 10

    The "token" is used by NM to desginate all file and RPC interactions tied
    to a given execution.

    This class will be called by the module's __main__.py file to:
     - read JSON from the NetMagus backend via the input-file if it exists
     - read in any previous state tied to the token/session
     - import the user's script/module and execute it's run() method
        - run() method must receive a NetMagusSession object as only arg
        - run() method may return Form or (Form, anyobject)
     - receive a Form (and a state object) as a return from the user's
       run() method
     - store any state object and send JSON response back to NetMagus backend


     The .start method is used to initiate the execution of the user's code
     in the formula.

     The user's code can use various attributes and methods of this session
     object to interact with the NetMagus server and its UI.

     The following attributes exist within each session object:

     nm_input:  holds the data entered by end-user on the NM ui
     user_state: holds any state data from previous formula steps

     The following methods exist within each session object for interaction
     with the NetMagus server:

     rpc_connect: opens a real-time RPC bus to the NM server
     rpc_disconnect: closes the formula's RPC connection to the NM server
     rpc_send:  sends a messsage to the NM server via RPC using this formula's
                current execution token
     rpc_receive:   retrieves any data pending on NM server for this formula's
                    execution token
     rpc_form_query:    sends a form to UI via RPC call and blocks until user
                        submits a response or timeout is exceeded

     The following objects can be sent to the NetMagus server for display in
     the UI:

     rpc_html:  used to send HTML based notices real-time to NM UI for display
                to the end-user
     form:  used to send a form composed of form component objects to ask an
            end-user for input

     The following objects within the sesion can be sent to the NetMagus UI
     inside a form object:

     textarea
     textinput
     radiobutton
     passwordinput
     dropdownmenu
     checkbox

    """

    def __init__(self, token, input_file, loglevel, script):
        """
        The netmagus package's main method will parse the CLI args passed from
        the NetMagus backend and instantiate a new NetMagusSession object used
        to manage the connection and data passing to/from the NetMagus backend.
        
        :param token: a randomized token used to associate with a given
                      formula execution, provided from NM
        :type token: str
        :param input_file: the abs path to an input JSON file from NM backend
        :type input_file: str
        :param loglevel: a value from 0-5 indicating the log level to use
                         for the debugger passed from NM backend
        :type loglevel: int
        :param script: the name of the user python module to import and call
                       the run() entry point method
        :type script: str
        :returns: The next operation to be executed when this one completes
        :rtype: netmagus.netop.NetOpStep
        """
        # the NM "token" used to differntiate every commandPath execution
        self.token = token
        # the JSON file sent from NM back-end as input to this execution
        self.input_file = input_file
        # the logging level set in the NM UI formula admin screen
        self.loglevel = loglevel
        # the name of the Python module in the formula's directory
        self.script = script
        # the session logger setup when self.start() is called
        self.logger = logging.getLogger(__name__)
        # nm_input stores the JSON file input from NetMagus backend
        self.nm_input = None
        # session state data to be used by multiple screen.Screen objects
        # if they need to store/pass persistent data between multiple screens
        self.session_data = None
        self.user_state = self.session_data  # legacy ref for old versions
        # Convenience methods for user script writers
        self.rpc_connect = netmagus.rpc.rpc_connect
        self.rpc_disconnect = netmagus.rpc.rpc_disconnect
        self.rpc_form = netmagus.form.Form
        self.rpc_html = netmagus.rpc.Html
        self.netopstep = netmagus.form.Form  # for legacy <v0.6.0 compatability
        self.form = netmagus.form.Form
        self.textarea = netmagus.form.TextArea
        self.textinput = netmagus.form.TextInput
        self.radiobutton = netmagus.form.RadioButton
        self.passwordinput = netmagus.form.PasswordInput
        self.dropdownmenu = netmagus.form.DropDownMenu
        self.checkbox = netmagus.form.CheckBox

    def rpc_send(self, message):
        """
        Send a message to the NetMagus backend via WAMP to the session's RPC
        target.

        This is a convenience method to handle the token manipulation for the
        session. See rpc.rpc_send method for full args
        :returns Nothing
        """
        netmagus.rpc.rpc_send(self.token, message)

    def rpc_receive(self):
        """
        Retrieve a message via WAMP from the session's RPC target on the
        NetMagus backend service.

        This is a convenience method to handle the token manipulation for the
        session.  See rpc.rpc_receive method for full args
        :returns Any response message currently available at the RPC target
        for this session
        """
        return netmagus.rpc.rpc_receive(self.token)

    def rpc_form_query(self, message, **kwargs):
        """
        Send a message to the NetMagus backend via WAMP to the session's RPC
        target, then poll the target for response data.

        This is a convenience method to handle token manipulation for the s
        ession.  See rpc.rpc_form_query for a full set of args
        :param message: an rpc.Message object to be sent to NetMagus backend
        :param kwargs: see rpc.rpc_form_query for full arg list
        :returns the response messsage at the target RPC target for this session
        """
        return netmagus.rpc.rpc_form_query(self.token, message, **kwargs)

    def rpc_html_clear(self):
        """
        Send a message to the NM backend to clear the UI's HTML pop-up
        display area.
        """
        self.rpc_send(netmagus.rpc.Html(append=False))

    def start(self):
        """
        Method to start the execution of user python module for the session

        :returns  returns a JSON result file and a Shelve to store a user state
        object
        """
        self.logger.setLevel(self.loglevel)
        self.__read_response_file()
        self.__read_state_file()
        formula_return = self.__run_user_script()
        self.__write_response_file(formula_return)
        self.__write_state_file(self.user_state)

    def __run_user_script(self):
        """
        Used by the start method to import and execute the user's Python module
        containing the formula logic

        :return: the netmagus.form.Form object returned by the user's module.
        """
        try:
            self.logger.debug('Attempting to import user module: '
                              '{}'.format(self.script))
            user_module = importlib.import_module(self.script)
            self.logger.debug('User module imported: {}'.format(user_module))
            self.logger.debug('Attempting to execute user module run() method')
            formula_return = user_module.run(self)
            if isinstance(formula_return, netmagus.form.Form):
                self.logger.debug('User module returned a form only')
                self.__fix_formcomponent_indexes(formula_return)
                return formula_return
            # allow for old formula format <v0.6.0 with tuple
            elif isinstance(formula_return, tuple):
                if isinstance(formula_return[0], netmagus.form.Form):
                    self.__write_state_file(formula_return[1])
                    return formula_return[0]
            else:
                raise TypeError('Formula files should return a '
                                'netmagus.form.Form object')
        except ImportError:
            raise ImportError('Unable to load user module: '
                              '{}'.format(self.script))
        except (Exception, NameError, IOError) as ex:
            self.logger.critical(
                'Error calling run() method defined in the target file: '
                '{}'.format(self.script))
            tb = traceback.format_exc()
            logging.exception(ex)
            htmlextrainfo = {
                'html': {
                    'printToUser': True,
                    'outputType': 'html',
                    'title': 'ERROR IN FORMULA',
                    'data': '<h3>This formula has encountered a critical error '
                            'and can not continue.  Please review the '
                            'traceback info and/or contact support for '
                            'assistance.</h3><br><br>Traceback info was: '
                            '<pre>{}</pre>'.format(tb)
                }
            }
            next_step = netmagus.form.Form(currentStep=999, dataValid=False,
                                           extraInfo=htmlextrainfo,
                                           disableBackButton=True,
                                           finalStep=True)
            return next_step

    def __read_response_file(self):
        """
        Read in the JSON response file from the NetMagus back-end.  These files
        are generated each time the NetMagus backend executes a commandPath to
        launch a task defined in a formula.  Examples would be when a user
        presses the SUBMIT button in the UI, a JSON file is generated by
        NetMagus and stored in a temp file to pass data to the Formula.
        """
        self.logger.debug('Reading JSON data from NetMagus request')
        try:
            with open(self.input_file) as data_file:
                self.nm_input = json.load(data_file)
            os.remove(self.input_file)  # remove file after reading it
        except IOError:
            self.logger.warn('Unable to access input JSON file {}'.format(
                self.input_file))
        except TypeError:
            self.logger.error('Unable to decode JSON data in {}'.format(
                self.input_file))

    def __read_state_file(self):
        """
        This method will retrieve any previous state data saved during this
        formula execution and store it internal as self.user_state where it
        can be used throughout the formula execution and serve as a target
        for persistent data storage throughout the formula's multiple
        execution steps.
        """
        state_file = self.input_file + '_State'
        try:
            with open(state_file, 'rb') as picklefile:
                self.user_state = pickle.load(picklefile)
                self.logger.debug('Formula state retrieved from '
                                  '{}'.format(state_file))
        except pickle.UnpicklingError:
            self.logger.info('The state file {} exists but does not '
                             'contain previous state from this formula '
                             'execution.  Setting state to '
                             'NONE'.format(state_file))
            self.user_state = None
        except IOError:
            self.logger.info('No _State file found from previous formula '
                             'execution steps. Setting state to NONE.')
            self.user_state = None

    def __write_response_file(self, response):
        """
        Store the returned Form into a Response file for NetMagus to read and
        process for execution of the next formula step
        """
        response_file = self.input_file + 'Response'
        self.logger.debug(
            'Target output JSON file will be: {}'.format(response_file))
        try:
            with open(response_file, 'w') as outfile:
                outfile.write(str(response))
        except IOError:
            self.logger.error('Unable to open target JSON Response file: '
                              '{}'.format(response_file))
            raise

    def __write_state_file(self, stateobject):
        """
        store the returned state object into a file for future operation
        steps to retrieve.  Formula creators can store an object in the
        sessions user_state attribute to have anyobject saved to disk and
        passed to the next formula execution step where it will be retrieved
        and stored in NetMagusSession.user_state for use by other formula code
        """
        state_file = self.input_file + '_State'
        self.logger.debug(
            'Target output shelve file will be: {}'.format(state_file))
        try:
            with open(state_file, 'wb') as picklefile:
                pickle.dump(stateobject, picklefile, protocol=-1)
                self.logger.debug('Formula state stored in '
                                  '{}'.format(state_file))
        except pickle.PickleError:
            self.logger.error('Error pickling state object')
            raise
        except IOError:
            self.logger.error('Unable to open target state file: '
                              '{}'.format(state_file))
            raise

    @staticmethod
    def __fix_formcomponent_indexes(form_obj):
        """
        This method is a temporary fix to append an index attribute to each
        form component to be sent to NetMagus as JSON.  Eventually this will
        be done in the NetMagus back-end upon receipt according to the order
        of the list of form controls.  For now these are being added here in
        the same fashion before being sent to the NetMagus back-end.
        :param form_obj: a netmagus.NetOpStep object to be serialized and
        sent to NetMagus
        """
        # TODO: REMOVE INDEX INCREMENTING ONCE PROBERT100 FIXES NM
        index_counter = 0
        for item in form_obj.form:
            setattr(item, 'index', index_counter)
            index_counter += 1

    def display_screen(self, screen):
        """
        Render a netmagus.screen.Screen object to the NetMagus UI for this
        session.

        You may optionally also pass in a function that returns a Screen object.
        The passed function will be called and if it returns a valid Screen
        instance it will be used.

        :param screen: the screen to activate in the UI
        :type screen: netmagus.screen.Screen
        :return: a final form to be shown at session completion
        :rtype: netmagus.form.Form
        """
        # validate type of screen
        if callable(screen):
            self.logger.debug('dispaly_screen executing callable {} to generate'
                              ' Screen'.format(screen))
            screen = screen()
        if not isinstance(screen, netmagus.screen.ScreenBase):
            raise TypeError('session.display argument is not '
                            'a valid Screen object')
        self.logger.debug('displaying screen {}'.format(screen))
        # set the screen's session attribute to this session
        screen.session = self
        try:
            # reset flag each time screen is displayed
            screen.input_valid = False
            while not screen.input_valid:
                self.logger.debug('sending form to UI')
                response = screen.session.rpc_form_query(screen.form)
                screen.user_input = response[
                    'wellFormatedInput']  # store user input
                # don't log actual user input since it may contain sensative
                # data that could be viewd in debug output or formula history
                # in the UI
                self.logger.debug('{} user input received with length {}'
                                  ''.format(screen.__class__.__name__,
                                            len(screen.user_input)
                                            )
                                  )
                screen.button_pressed = response.get('pressedButton')
                # handle the button press to apply next/back/cancel logic
                screen.process_button()
            # clear HTML pop-up screen once valid data received
            screen.session.rpc_send(screen.session.rpc_html(append=False))
            if screen.next_screen:
                self.logger.debug('Data validation passed, '
                                  'processing next screen')
                self.display_screen(screen.next_screen)
            else:
                self.logger.debug('No next_screen set, returning')
        except netmagus.screen.CancelButtonPressed:
            self.rpc_html_clear()
            screen.handle_cancel_button()
            raise
        except netmagus.screen.BackButtonPressed:
            screen.handle_back_button()
            self.display_screen(screen.back_screen)
