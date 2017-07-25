#!usr/bin/python
#  main.py


from meet.terminal.terminal import get_user_input
from meet.interface.api import GoogleAPI
from meet.google.gcalendar import gCalendar
from meet.functions.functions import write_md_to_file
from meet.functions.functions import write_html_to_file
from meet.functions.functions import open_file_to_edit


def main():
    #  instantiate a google api object
    google_api = GoogleAPI()

    #  use terminal to parse user input
    args = get_user_input()

    #  api call to google to get a calendar object
    meetings = google_api.get_meeting()

    #  create a calendar object
    gcalendar = gCalendar()
    gcalendar.new_meeting(meetings)

    if args.markdown:
        md_path = write_md_to_file(gcalendar, args)
        open_file_to_edit('markdown', md_path)

    # if args.google and args.share:
    #     pass

    if args.google:
        file_path, file_name = write_html_to_file(gcalendar, args)
        file_id = google_api.create_google_doc(file_path, file_name)
        open_file_to_edit('google', file_id)


if __name__ == '__main__':
    main()
