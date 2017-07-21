
import logging
import ttk
from Queue import Queue, Empty
from Tkconstants import E, W, EW, NSEW, NORMAL, DISABLED, END

from frame.frame import BaseFrame
from widget.scroll import TextScroll
from logging_helper import setup_log_format


class TextHandler(logging.Handler):

    """This class sets up a custom log Handler that allows you to log to a Tkinter Text or ScrolledText widget"""

    def __init__(self,
                 text,
                 *args,
                 **kwargs):

        super(TextHandler, self).__init__(*args, **kwargs)

        self.text = text
        self.setFormatter(setup_log_format())
        self.setup_line_colours()
        self.log_queue = Queue()

    def handle(self, record):

        rv = self.filter(record)

        if rv:
            self.log_queue.put(record)

        return rv

    def emit(self, record):

        msg = (self.format(record)
               .replace(u'\"', u'"')
               .replace(u'"', u'\"')
               .replace(u"\'", u"'")
               .replace(u'"', u"\'"))  # Might be a better way to do this
                                       # Needed to do this to avoid an issue
                                       # with self.text.insert with there was
                                       # a single "

        def append():

            self.text.configure(state=NORMAL)

            try:
                colour_key = msg.split(u' - ')[1][:7].strip()
                self.text.insert(END, msg + u'\n', colour_key)
            except Exception as e:
                logging.error(u'Error inserting: [{msg}]'
                              .format(msg = msg))
                logging.error(e)
            self.text.configure(state=DISABLED)

            # Autoscroll to the bottom (shifted for the blank line)
            self.text.yview(float(self.text.index("end-1c linestart")) - 1)

        # This is necessary because we can't modify the Text from other threads
        # and we don't want this to be blocking!
        self.text.after(0, append)

    def clear(self, start=1.0, end=END):
        self.text.configure(state=NORMAL)
        self.text.delete(start, end)
        self.text.configure(state=DISABLED)

    def setup_line_colours(self):

        tag_colours = {u'DEBUG': u'blue',
                       u'INFO': u'black',
                       u'WARNING': u'orange',
                       u'ERROR': u'red',
                       u'CRITICAL': u'red'}

        for colour in tag_colours:
            self.text.tag_configure(colour, foreground=tag_colours[colour])

    def poll(self):

        try:
            record = self.log_queue.get(timeout=0.01)

            self.emit(record=record)

            self.log_queue.task_done()

        except Empty:
            pass


class LogFrame(BaseFrame):

    def __init__(self,
                 *args,
                 **kwargs):

        self.__enable_poll = False

        BaseFrame.__init__(self, *args, **kwargs)

        BUTTON_WIDTH = 20

        LEFT_COL = self.column.start()
        MIDDLE_COL = self.column.next()
        RIGHT_COL = self.column.next()
        self.columnconfigure(RIGHT_COL, weight=1)

        LEVEL_ROW = self.row.next()

        ttk.Label(self, text=u'Log Level:').grid(row=LEVEL_ROW, column=LEFT_COL, sticky=W)

        self.level_list = [u'DEBUG',
                           u'INFO',
                           u'WARNING',
                           u'ERROR',
                           u'CRITICAL']

        self.__level_var = self.string_var(value=u'INFO',
                                           trace=self.__level_change)
        self.__level = self.combobox(textvariable=self.__level_var,
                                     values=self.level_list,
                                     row=LEVEL_ROW,
                                     column=MIDDLE_COL,
                                     sticky=W)

        self.__clear_button, self.__clear_button_tooltip = self.button(state=NORMAL,
                                                                       text=u'Clear',
                                                                       width=BUTTON_WIDTH,
                                                                       command=self.__clear,
                                                                       row=LEVEL_ROW,
                                                                       column=RIGHT_COL,
                                                                       sticky=E,
                                                                       tooltip=u'Clear the log window')

        CONFIG_ROW = self.row.next()
        self.rowconfigure(CONFIG_ROW, weight=1)
        self.log_text = TextScroll(self, state=DISABLED)
        self.log_text.grid(row=CONFIG_ROW, column=LEFT_COL, columnspan=3, sticky=NSEW)
        self.log_text.configure(font=u'TkFixedFont')

        # Create textLogger
        self.text_handler = TextHandler(self.log_text)
        self.text_handler.setLevel(self.__level_var.get())

        # Add the handler to root logger
        logger = logging.getLogger()
        logger.addHandler(self.text_handler)

        self.__enable_poll = True

    def __level_change(self):
        self.text_handler.setLevel(self.__level_var.get())

    def __clear(self):
        self.text_handler.clear()

    def poll(self):
        if self.__enable_poll:
            self.text_handler.poll()


class LogTickerFrame(BaseFrame):

    def __init__(self,
                 log_level=u'INFO',
                 *args,
                 **kwargs):

        self.__enable_poll = False

        BaseFrame.__init__(self, height=23, *args, **kwargs)

        self.grid(sticky=EW)
        self.grid_propagate(0)

        LEFT_COL = self.column.start()
        self.columnconfigure(LEFT_COL, weight=1)

        TEXT_ROW = self.row.start()
        self.rowconfigure(TEXT_ROW, weight=1)

        # Create the text
        self.log_text = TextScroll(self,
                                   state=DISABLED,
                                   vbar=False,
                                   hbar=False)
        self.log_text.grid(row=TEXT_ROW, column=LEFT_COL, sticky=EW)
        self.log_text.configure(font=u'TkFixedFont', background=u'#E7E7E7')

        # Create textLogger
        self.text_handler = TextHandler(self.log_text)
        self.text_handler.setFormatter(self.setup_ticker_format())
        self.text_handler.setLevel(log_level)

        # Add the handler to root logger
        logger = logging.getLogger()
        logger.addHandler(self.text_handler)

        self.__enable_poll = True

    def poll(self):
        if self.__enable_poll:
            self.text_handler.poll()

    @staticmethod
    def setup_ticker_format():

        # Setup formatter to define format of log messages
        format_string = u'{timestamp} - {level} : {msg}'.format(timestamp=u'%(asctime)s',
                                                                level=u'%(levelname)-7s',
                                                                msg=u'%(message)s')

        log_formatter = logging.Formatter(fmt=format_string,
                                          datefmt=u'%H:%M:%S')

        return log_formatter

