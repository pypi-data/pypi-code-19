"""
Written by: Ian Doarn

Stock page

Interacts with the stock page and its sub pages
such as the product chooser
"""
from zbsmsa.utils.decorators import deprecated
from zbsmsa.utils.utilities import load_selectors, get_range_from_results, \
    concat_selectors, read_table
from zbsmsa.utils.constants import DEFAULT_AUTO_SOURCE_IGNORES, ENTER_KEY
from zbsmsa.utils.exceptions import ItemAddError, \
    SelectionError, MutationError, StockTableError
import time
from bs4 import BeautifulSoup


class Stock:
    """
    Stock class
    
    requires the site class to be passed in as an object
    """
    def __init__(self, site):
        """
        :param site: Site class object
        """
        self.site = site

        # Load necessary selectors
        self.stock_page_selectors = load_selectors('stockTab.json')
        self.product_chooser_selectors = load_selectors('prodChooser.json')
        self.stock_page_table_selectors = load_selectors('stockTabTable.json')
        self.mutate_selectors = load_selectors('stockTabMutate.json')

        # store data from table
        self.current_table_data = []
        self.current_table_text = []

        # Button paths
        self.__auto_source_invalid_kits = self.stock_page_table_selectors["stAutoSourceInvalidKits"]
        self.__select_all_rows = self.stock_page_table_selectors["stTableSelectAll"]
        self.__tab_button = self.stock_page_selectors["stStockTabButton"]
        self.__tab_search = self.stock_page_selectors["stStockTabSearchButton"]
        self.__tab_mutate = self.mutate_selectors["stMutateButton"]
        self.__tab_product_chooser = self.product_chooser_selectors["prodchooserSelect"]

        # Other Paths
        self.__auto_source_invalid_kits_prompt = self.stock_page_table_selectors["stAutoSourceInvalidKitsErrorPrompt"]

    def stock_tab(self):
        """
        Stock tab button
        :return: 
        """
        self.site.wait.clickable(self.__tab_button)

    def stock_tab_search(self):
        """
        Stock tab search button
        :return: 
        """
        self.site.wait.clickable(self.__tab_search)

    def stock_tab_mutate(self):
        """
        Stock tab mutate button
        :return: 
        """
        self.site.wait.clickable(self.__tab_mutate)

    def stock_tab_product_chooser(self):
        """
        Go to the stock tab product chooser
        but go to the stock tab first just in case we aren't there
        :return: 
        """
        self.stock_tab()
        self.site.wait.clickable(self.__tab_product_chooser)

    @deprecated('This method will be deprecated in upcoming an version')
    def format_current_table_data_text(self):
        """
        !!!THIS METHOD IS BEING DEPRECATED!!!
        !!!DO NOT USE IT!!!

        Format text from row data into 
        a dictionary current_table_text
        
        :return: 
        """

        def __format(row):
            _row_text = row['text'].split('|')[1:]

            f = {'product': _row_text[0],
                 'description': _row_text[1],
                 'lot_serial': _row_text[2],
                 'contained_in': _row_text[5],
                 'container_type': _row_text[4],
                 'location': _row_text[8],
                 'location_type': _row_text[7],
                 'qoh': _row_text[9],
                 'qav': _row_text[10],
                 'qr': _row_text[11],
                 'zsms_hold': True if _row_text[12] == 'Yes' else False}

            return f

        __data = []

        for r in self.current_table_data:
            __data.append({'row': r['row'],
                           'text': __format(r)})
        self.current_table_text = __data
        return __data

    def mutate_stock(self, note, qty="1", click_ok_on_error=True):
        """
        Mutates stock that is selected to 
        different inventory types
        
        :param note: Note to input 
        :param qty: quantity of stock to mutate, default @ "1"
        :param click_ok_on_error: Click ok even when an error occurs. default @ True
        :return: 
        """

        # Click mutate button
        self.stock_tab_mutate()

        # input quantity
        self.site.wait.send_keys_to(qty, self.mutate_selectors["stMutateQuantity"])

        # input note
        self.site.wait.send_keys_to(note, self.mutate_selectors["stMutateNote"])

        # Click save
        self.site.wait.clickable(self.mutate_selectors["stMutateSavebutton"])

        # Wait for a little bit
        time.sleep(2)

        try:
            # We check to see if we the message box 'Stocks has been mutated.' is visible
            message_box = self.site.get_text_from_site_error(
                "body > div.gwt-PopupPanel > div > div > table > tbody > tr > td")
        except Exception as error:
            print(error)
            # Some other type of error / message occurred or another hidden element
            # owns the div.gwt-PopupPanel. Sometimes multiple ones exist
            pass
        else:
            for sub_element in message_box['tags']:
                if sub_element.text.__contains__('Stocks has been mutated.'):
                    # click ok on our message, and return to calling method
                    message_box['tags'][2].click()
                    return True

        # Otherwise we try to find out what happened
        # We have no way of knowing which nth div element the error will be.
        # Generally it is 12 or 13
        for nth in range(12, 14):
            try:
                message_box = self.site.get_text_from_site_error(
                    "body > div:nth-child({}) > div > div > table > tbody > tr > td".format(nth))
            except Exception as error:
                print(error)
                # Element did not exist, pass and keep going
                pass
            else:
                if click_ok_on_error:
                    for tag in message_box['tags']:
                        if tag.text.lower() == 'ok':
                            try:
                                tag.click()
                                self.site.wait.clickable(
                                    self.mutate_selectors["stMutateCancelButton"])
                            except Exception as error:
                                print(error)
                                raise MutationError(msg="Unable to accept error. "
                                                        "ERROR: {}".format(message_box['tags'][0].text))
                            else:
                                return True

                # TODO: Fix accept_and_raise to click the element on the page then raise an error
                # TODO: Currently throws (stale element reference)
                # if accept_and_raise_error:
                #     for tag in message_box['tags']:
                #         error_text = message_box['tags'][0].text.replace('\n', '')
                #         if tag.text.lower() == 'ok':
                #             error = MutationError(msg='An error occurred while mutating stock. {}'.format(
                #                 error_text),
                #                 reason=error_text)
                #             try:
                #                 tag.click()
                #                 self.site.wait.clickable(
                #                     self.mutate_selectors["stMutateCancelButton"])
                #                 raise error
                #             except Exception:
                #                 raise MutationError(msg="Unable to accept error. "
                #                                         "ERROR: {}".format(message_box['tags'][0].text))

                # Error message box found and no specific action was specified,
                # Raise error with message boxes information
                raise MutationError(error=message_box)

        # Mutation fail somewhere in the method and no error was prompted,
        # return false to indicate that no site error occurred but the mutation
        # still failed.
        return False

    def select_row(self, r):
        """
        Select a specific row on the table
        
        :param r: Row number 
        :return: 
        """
        if r == 0:
            raise ValueError("row number cannot be 0")

        first_row = self.stock_page_table_selectors["stTableCheckBoxInit"]
        even_row = concat_selectors(self.stock_page_table_selectors["stTableCheckBoxRowEvenFront"],
                                    str(r),
                                    self.stock_page_table_selectors["stTableCheckBoxRowEvenBack"])
        odd_row = concat_selectors(self.stock_page_table_selectors["stTableCheckBoxRowOddFront"],
                                   str(r),
                                   self.stock_page_table_selectors["stTableCheckBoxRowOddBack"])
        # First row
        if r == 1:
            self.site.wait.clickable(first_row)
            return True
        elif r % 2 == 0:
            # is an even row
            self.site.wait.clickable(even_row)
            return True
        elif r % 2 != 0:
            # is an odd row
            self.site.wait.clickable(odd_row)
            return True

        # Was unable to select row
        raise SelectionError('stock table row [{}]'.format(str(r)))

    def __is_table_multi_page(self):
        """
        Check if table has more than one page
        :return: 
        """
        if self.get_table_results()[-1:] == '+':
            return True
        else:
            return False

    def get_table_results(self):
        """
        Get the range from results of the table
        :return: 
        """
        try:
            r = self.site.get_inner_html(self.stock_page_selectors["stStockTabResults"])
            return r
        except Exception as error:
            print(error)
            raise StockTableError(msg='Table not loaded / could not be found')

    def change_table_page(self, direction, sleep_for=1, wait_after_change=True):
        """
        Change the page of the stock table
        
        + is next page
        - is previous page
        
        :param direction: + or -
        :param sleep_for: how long to wait after changing page
        :param wait_after_change: wait after page changes
        :return: if successful
        """
        _next = self.stock_page_table_selectors["stTableNextPage"]
        _previous = self.stock_page_table_selectors["stTablePreviousPage"]
        if direction == '-':
            try:
                self.site.wait.clickable(_previous)
                time.sleep(sleep_for) if wait_after_change else None
                return True
            except Exception as error:
                raise StockTableError(msg='Could not go to previous page [{}]'.format(error))
        if direction == '+':
            if self.__is_table_multi_page():
                try:
                    self.site.wait.clickable(_next)
                    time.sleep(sleep_for) if wait_after_change else None
                    return True
                except Exception as error:
                    raise StockTableError(msg='Could not go to next page [{}]'.format(error))
            else:
                return False

    def auto_source_invalid_kits(self, ignore_values=DEFAULT_AUTO_SOURCE_IGNORES):
        """
        Auto Source all invalid kits
        
        if any rows contain:
            1. text from ignore_values 
            2. are on ZSMS Hold
            3. have a QR > 0
        they will be ignored
        
        :param ignore_values: List of strings to check for in rows text
        :return: None
        """

        # Select entire table
        self.site.wait.clickable(self.__select_all_rows)

        rows_to_dismiss = []

        # Parse the table. If any of the conditions return
        # true then omit that row
        for row in self.parse_table():
            if any(val in row.values() for val in ignore_values):
                rows_to_dismiss.append(int(row['row']))
            elif any(substring in row['container'] for substring in ignore_values):
                rows_to_dismiss.append(int(row['row']))
            elif row['zsms_hold'].lower() == 'yes':
                rows_to_dismiss.append(int(row['row']))
            elif int(row['qr']) > 0:
                rows_to_dismiss.append(int(row['row']))
            else:
                pass

        # Deselect all omitted rows
        for r in rows_to_dismiss:
            self.select_row(r)

        # Click Auto Source
        self.site.wait.clickable(self.__auto_source_invalid_kits)

        try:
            self.site.wait.chain_send_keys_to_driver(ENTER_KEY, wait_for_element=True,
                                                     element=self.__auto_source_invalid_kits_prompt)
        except Exception:
            raise SelectionError('Could not close prompt')

    def parse_table(self):
        """
        Parse table for information

        :return: List of OrderedDict's for each row in the table
        """
        return read_table(BeautifulSoup(self.site.page_source(), "lxml"), 'stock')

    @deprecated('This method will be deprecated in upcoming an version. Use parse_table() method.')
    def iterate_search_table(self, multi_page=False, text_only=False):
        """
        !!!THIS METHOD IS BEING DEPRECATED!!!
        !!!DO NOT USE IT!!!
        Iterates stock search table returning each entry
        
        !!!Browser window MUST be maximized for this to properly work!!!
        
        Process:
            1. Get results from bottom of page an format
            2. Get range with get_range_from_results
            3. iterate table
            4 iterate each rows tr html element and add it to the list trs keeping
             track of the row and the tr element
            5. for each tr in trs, we are going to get each element by the
             tag 'td'
            6. Then attempt to get the text from each element, if there is none,
             append 'None'
            7. Add that to the list of data, each entry in the list is a dictionary
             with the format {'row': row number, 'tr': table row, 'td': table cell, 'text': concat cell text}

        :return:
        """

        if self.get_table_results().lower() == "no records":
            raise ValueError("No Records Found")

        if multi_page:
            mp_results = self.get_table_results()
            # Get min and max range of table
            min_y, max_y = get_range_from_results(mp_results, multi_page=multi_page)

            trs = []
            # iterate table, add 1 to max since range is 0 indexed
            for y in range(min_y, max_y + 1):
                front = self.stock_page_table_selectors["stTableRowFront"]
                back = self.stock_page_table_selectors["stTableRowBack"]

                try:
                    # attempted to get the table row from the current row
                    for tr in self.site.driver.find_elements_by_css_selector("{}{}{}".format(front, str(y), back)):
                        trs.append({'row': y, 'tr': tr})
                except Exception as error:
                    print(error)

            data = []
            # iterate our list of table rows
            for tr in trs:
                # Get the row number
                # the table row object
                # and te table cells from the row
                row = tr['row']
                tr = tr['tr']
                td = tr.find_elements_by_tag_name('td')

                info = []
                for element in td:
                    # for each cell in the row, attempt to get its text
                    try:
                        info.append(element.text)
                    # otherwise, set the text to none
                    except Exception as error:
                        print(error)
                        info.append('None')

                text = '|'.join(info)
                if not text_only:
                    # Add the data to our list
                    data.append({'row': row, 'tr': tr, 'td': td, 'text': text})

                else:
                    # Format the data to a proper dictionary
                    _row_text = text.split('|')[1:]

                    f = {'product': _row_text[0],
                         'description': _row_text[1],
                         'lot_serial': _row_text[2],
                         'contained_in': _row_text[5],
                         'container_type': _row_text[4],
                         'location': _row_text[8],
                         'location_type': _row_text[7],
                         'qoh': _row_text[9],
                         'qav': _row_text[10],
                         'qr': _row_text[11],
                         'zsms_hold': True if _row_text[12] == 'Yes' else False}

                    data.append({'row': row, 'text': f})

            if text_only:
                self.current_table_text = data

            self.current_table_data = data
            return True

        else:
            # Get min and max range of table
            min_y, max_y = get_range_from_results(self.get_table_results())

            trs = []
            # iterate table, add 1 to max since range is 0 indexed
            for y in range(min_y, max_y + 1):
                front = self.stock_page_table_selectors["stTableRowFront"]
                back = self.stock_page_table_selectors["stTableRowBack"]

                try:
                    # attempted to get the table row from the current row
                    for tr in self.site.driver.find_elements_by_css_selector("{}{}{}".format(front, str(y), back)):
                        trs.append({'row': y, 'tr': tr})
                except Exception as error:
                    print(error)

            data = []
            # iterate our list of table rows
            for tr in trs:
                # Get the row number
                # the table row object
                # and te table cells from the row
                row = tr['row']
                tr = tr['tr']
                td = tr.find_elements_by_tag_name('td')

                info = []
                for element in td:
                    # for each cell in the row, attempt to get its text
                    try:
                        info.append(element.text)
                    # otherwise, set the text to none
                    except Exception as error:
                        print(error)
                        info.append('None')

                text = '|'.join(info)
                if not text_only:
                    # Add the data to our list
                    data.append({'row': row, 'tr': tr, 'td': td, 'text': text})

                else:
                    # Format the data to a proper dictionary
                    _row_text = text.split('|')[1:]

                    f = {'product': _row_text[0],
                         'description': _row_text[1],
                         'lot_serial': _row_text[2],
                         'contained_in': _row_text[5],
                         'container_type': _row_text[4],
                         'location': _row_text[8],
                         'location_type': _row_text[7],
                         'qoh': _row_text[9],
                         'qav': _row_text[10],
                         'qr': _row_text[11],
                         'zsms_hold': True if _row_text[12] == 'Yes' else False}

                    data.append({'row': row, 'text': f})

            if text_only:
                self.current_table_text = data

            self.current_table_data = data
            return True


class ProductChooser:
    """
    Interacts with the Stock page product chooser
    """
    def __init__(self, stock_obj):
        """
        :param stock_obj: Stock class object
        """
        self.stock = stock_obj
        self.site = stock_obj.site
        self.driver = stock_obj.site.driver
        self.prod_selectors = self.stock.product_chooser_selectors

    def search(self, item):
        """
        Searches for item using product chooser
        :param item: item to search for
        :return: 
        """
        self.site.wait.send_keys_to(item, self.prod_selectors["prodchooserSearchBar"])
        self.site.wait.clickable(self.prod_selectors["prodchooserSearchButton"])

    def finish(self):
        """
        Click finish and return to stock page
        :return: None
        """
        self.site.wait.clickable(self.prod_selectors["prodchooserFinishButton"])

    def add(self, product_number):
        """
        Adds item to the product chooser
        
        First we iterate the table, creating our data.
        
        Then we check what row is came from, the row it cam from matters since
        the css selectors mutate depending on the row. We check to 
        see if it is the first row, an odd row, or an even row. We then try each selector
        combination.
        
        If we reach the end of if statement or the for loop
        then we raise an error since we were not able 
        to successfully add the item.
        
        :param product_number: Item to search for
        :return: Return only if item is successfully added
        """

        # collect our table data by iterating the table
        data = self.iterate_search_table()

        for row in data:
            r = row['row']
            text = row['text'].replace(' ', '').split('|')

            try:
                results = [True for x in text if x == product_number]
                if len(results) != 0 and results[0] is True:
                    # Build our selectors
                    basic_selector = self.prod_selectors["prodchooserAdd"]
                    primary_selector = concat_selectors(self.prod_selectors["prodChooserAddLastFront"],
                                                        str(r),
                                                        self.prod_selectors["prodChooserAddLastBack"])
                    secondary_selector = concat_selectors(self.prod_selectors["prodChooserAddFront"],
                                                          str(r),
                                                          self.prod_selectors["prodChooserAddEvenBack"])

                    if r == 1:
                        # it is on the first row
                        self.site.wait.clickable(basic_selector)
                        return
                    elif r % 2 == 0:
                        # It is on an even row but the selectors
                        # for even rows mutate
                        # So we have to try these two combinations
                        try:
                            self.site.wait.clickable(primary_selector)
                            return
                        except Exception as error:
                            print(error)
                            self.site.wait.clickable(secondary_selector)
                            return
                    elif r % 2 != 0:
                        # it is on an odd row
                        self.site.wait.clickable(primary_selector)
                        return

                    # should only get here if we cant add item
                    # or the css path on the site has mutated in some way
                    raise ItemAddError(product_number)
                else:
                    continue
            except Exception as error:
                raise ItemAddError(product_number, msg='Unable to find item in table. ERROR: {}'.format(error))

        # No match was found
        raise ItemAddError(product_number, msg='Unable to find item in table.')

    @deprecated('This method will be deprecated in upcoming an version. Use parse_table() method.')
    def iterate_search_table(self):
        """
        !!!THIS METHOD IS BEING DEPRECATED!!!
        !!!DO NOT USE IT!!!

        Iterates product chooser table returning each entry
        
        !!!Browser window MUST be maximized for this to properly work!!!
        
        Process:
            1. Get results from bottom of page an format
            2. Get range with get_range_from_results
            3. iterate table
            4 iterate each rows tr html element and add it to the list trs keeping
             track of the row and the tr element
            5. for each tr in trs, we are going to get each element by the
             tag 'td'
            6. Then attempt to get the text from each element, if there is none,
             append 'None'
            7. Add that to the list of data, each entry in the list is a dictionary
             with the format {'row': row number, 'tr': table row, 'td': table cell, 'text': concat cell text}
            
        :return: Data list
        """

        results = self.site.get_inner_html(self.prod_selectors["prodChooserResults"])

        # Get min and max range of table
        min_y, max_y = get_range_from_results(results)

        trs = []
        # iterate table, add 1 to max since range is 0 indexed
        for y in range(min_y, max_y + 1):
            front = self.prod_selectors["prodChooserTRpathFront"]
            back = self.prod_selectors["prodChooserTRpathBack"]

            try:
                # attempted to get the table row from the current row
                for tr in self.driver.find_elements_by_css_selector("{}{}{}".format(front, str(y), back)):
                    trs.append({'row': y, 'tr': tr})
            except Exception as error:
                print(error)

        data = []
        # iterate our list of table rows
        for tr in trs:
            # Get the row number
            # the table row object
            # and the table cells from the row
            row = tr['row']
            tr = tr['tr']
            td = tr.find_elements_by_tag_name('td')

            info = []
            for element in td:
                # for each cell in the row, attempt to get its text
                try:
                    info.append(element.text)
                # otherwise, set the text to none
                except Exception as error:
                    info.append('None')
                    print(error)

            # Add the data to our list
            data.append({'row': row, 'tr': tr, 'td': td, 'text': '|'.join(info).replace(' ', '')})

        return data
