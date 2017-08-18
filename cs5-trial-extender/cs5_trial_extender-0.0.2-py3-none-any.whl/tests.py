from cs5_trialextender.exceptions import InvalidConfigException, ExpirationDateExeption, TrialSerialNumberException, InvalidConfigFile
from cs5_trialextender.main import validate_config_xml, trial_extender
from cs5_trialextender.run import run, cli_help
from xml.etree import ElementTree as et
from os import pardir, path
import unittest

class TestXmlValidation(unittest.TestCase):
    '''Handle xml files and folder validation tests'''

    valid_file_folder_sample = path.join(path.join(path.dirname(path.abspath(__file__)), pardir), 'test_files\\valid_file') # same as "../test_files/valid_file"
    invalid_file_folder_sample = path.join(path.join(path.dirname(path.abspath(__file__)), pardir), 'test_files\\invalid_file') # same as "../test_files/invalid_file"
    this_folder = path.dirname(path.abspath(__file__))
    
    def test_valid_file_and_folder(self):
        xml = et.parse(path.join(self.valid_file_folder_sample,'application.xml')).getroot() 
        xml_text = et.tostring(xml, encoding='utf8', method='xml')
        self.assertEqual(et.tostring(validate_config_xml(self.valid_file_folder_sample).getroot(), encoding='utf8', method='xml'), xml_text)
        
    def test_invalid_file(self):
        with self.assertRaises(InvalidConfigFile):
            trial_extender(path=self.invalid_file_folder_sample)

    def test_invalid_folder(self):
        folder = path.join(self.this_folder,'inexistent_folder')
        with self.assertRaises(InvalidConfigFile):
            trial_extender(path=folder)

class TestXmlHandle(unittest.TestCase):
    '''Handle tests of changing data and save xml file'''

    application_folder = path.join(path.join(path.dirname(path.abspath(__file__)), pardir), 'test_files\\valid_file')
    invalid_application_folder = path.join(path.join(path.dirname(path.abspath(__file__)), pardir), 'test_files\\invalid_file')

    def test_change_serial(self):
        '''Test changing only the serial for 10 times'''
        for i in range(0,10):
            # Keep old values for comparission
            old_xml = et.parse(path.join(self.application_folder,'application.xml')).getroot() 
            old_xml_text = et.tostring(old_xml, encoding='utf8', method='xml')

            # Check if command runs
            trial_extender(self.application_folder, extend_date=False, replace_serial=True)
            self.assertTrue

            # Check if old file is equal to application_old.xml
            copy_old_xml = et.parse(path.join(self.application_folder,'application_old.xml')).getroot() 
            copy_old_xml_text = et.tostring(copy_old_xml, encoding='utf8', method='xml')
            self.assertEqual(copy_old_xml_text, old_xml_text)

    def test_change_data_whitout_xml_field(self):
        '''Test changing only the date when there is no date field on xml'''
        with self.assertRaises(ExpirationDateExeption):
            trial_extender(path=self.application_folder, extend_date=True, replace_serial=False)

    def test_change_serial_when_xml_not_valid(self):
        '''Test changing serial number when the xml isn't valid'''
        with self.assertRaises(InvalidConfigFile):
            trial_extender(path=self.invalid_application_folder, extend_date=False, replace_serial=True)

class TestRun(unittest.TestCase): 
    '''Test function RUN'''

    def test_arg_path_1(self):
        '''Test case the path was supplied using "path=c:/~"'''
        args = ['', 'path=c:/temp/inexistent_folder']
        with self.assertRaises(InvalidConfigFile):
            run(*args, verbose=False)

    def test_arg_path_2(self):
        '''Test case the path was supplied using "c:/~"'''
        args = ['', 'c:/temp/inexistent_folder']
        with self.assertRaises(InvalidConfigFile):
            run(*args, verbose=False)

    def test_kwargs_on_run(self):
        '''Test key arguments on run()'''
        args = ['', 'c:/temp/inexistent_folder', 'extend_date=True'] 
        with self.assertRaises(InvalidConfigFile):
            run(*args, verbose=False)
        
        args.append('new_date=2018/8/8')
        with self.assertRaises(InvalidConfigFile):
            run(*args, verbose=False)
        
        args.append('replace_serial=False')
        with self.assertRaises(InvalidConfigFile):
            run(*args, verbose=False)

if __name__ == '__main__':
    unittest.main()
