#!usr/bin/python
#  main.py


from meet.terminal.terminal import get_user_input
from meet.interface.api import GoogleAPI
from meet.google.gcalendar import gCalendar
from meet.functions.functions import write_md_to_file
from meet.functions.functions import write_html_to_file
from meet.functions.functions import open_file_to_edit
from meet.functions.functions import check_for_client_secret
from meet.functions.functions import launch_readme_in_browser
from meet.config.config import AppConf


def main():
    # check for an existing configuration file
    app_conf = AppConf()

    # check to see if user has their own client secret for google api
    cs_status = check_for_client_secret(app_conf)
    if not cs_status:
        print('Please see the README.md file to setup your Google oauth 2.0\n' +
              'credentials.  Follow the setup instructions, then launch the\n' +
              'application again.')
        launch_readme_in_browser()

    #  instantiate a google api object
    google_api = GoogleAPI(app_conf)

    #  use terminal to parse user input
    args = get_user_input()

    #  api call to google to get a calendar object
    meetings = google_api.get_meeting()

    #  create a calendar object
    gcalendar = gCalendar()
    gcalendar.new_meeting(meetings)

    if args.markdown:
        md_path = write_md_to_file(gcalendar, args)
        open_file_to_edit('markdown', md_path, app_conf)

    # if args.google and args.share:
    #     pass

    if args.google:
        file_path, file_name = write_html_to_file(gcalendar, args)
        file_id = google_api.create_google_doc(file_path, file_name)
        open_file_to_edit('google', file_id, app_conf)


if __name__ == '__main__':
    main()
