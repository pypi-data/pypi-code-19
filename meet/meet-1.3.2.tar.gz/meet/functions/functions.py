#!usr/bin/python
#  functions.py

import datetime
import sys
import os
import os.path
import webbrowser


def write_md_to_file(gcalendar, args, app_conf):
    for meeting in gcalendar.meetings:
        markdown_filename = '{} - {}.md'.format(
            meeting.meeting['start_date'],
            meeting.meeting['summary'])
        hr = '_ _ _\n\n'
        chars_to_remove = dict((ord(char), None) for char in '\\/*?:"<>|')
        clean_md_filename = markdown_filename.translate(chars_to_remove)
        final_file = create_os_nuetral_filepath(clean_md_filename, app_conf)
        f = open(final_file, 'w')
        f.write('# {}\n\n'.format(meeting.meeting['summary']))
        f.write('**Organizer**: {}\n\n'.format(
            meeting.meeting['organizer']
        ))
        f.write('**Start**: {} - {}  | \
                **End**: {} - {}  | \
                **Location**: {}\n\n'.format(
            meeting.meeting['start_date'],
            meeting.meeting['start_time'],
            meeting.meeting['end_date'],
            meeting.meeting['end_time'],
            meeting.meeting['location']
        ))
        f.write(hr)
        f.write('## Notes:\n\n')
        f.write('1. take notes here\n\n')
        f.write(hr)
        f.write('## Description:\n\n{}\n\n'.format(
            meeting.meeting['description']
        ))
        f.write(hr)
        f.write('**Calendar link**: {}\n\n'.format(
            meeting.meeting['html_link']
        ))
        f.write('**Attendees**:\n\n')
        att_build = 'Email | Status\n\n'
        attendee_check = meeting.meeting['attendees']
        if attendee_check == 'No attendees':
            f.write(attendee_check)
        else:
            for attendee in meeting.meeting['attendees']:
                email = attendee.get('email')
                response_status = attendee.get('responseStatus')
                if 'resource' not in email:
                    att_build = att_build + '{} | {}\n\n'.format(
                        email, response_status
                    )
            f.write(att_build)
        f.close()
        return final_file


def write_html_to_file(gcalendar, args, app_conf):
    for meeting in gcalendar.meetings:
        html_filename = '{} - {}'.format(
            meeting.meeting['start_date'],
            meeting.meeting['summary']
        )
        chars_to_remove = dict((ord(char), None) for char in '\\/*?:"<>|')
        file_name = html_filename.translate(chars_to_remove)
        file_path = create_os_nuetral_filepath(file_name, app_conf)
        f = open(file_path, 'w')
        f.write('<h1>{}</h1>'.format(meeting.meeting['summary']))
        f.write('<hr><br>')
        f.write('<br><p><b>Organizer</b>: {}</p><br>'.format(
            meeting.meeting['organizer']
        ))
        f.write('<b>Start</b>: {} - {} | <b>End</b>: {} - {} | \
                 <b>Location</b>: {}<br>'.format(
            meeting.meeting['start_date'],
            meeting.meeting['start_time'],
            meeting.meeting['end_date'],
            meeting.meeting['end_time'],
            meeting.meeting['location']
        ))
        f.write('<hr><br>')
        f.write('<h2>Notes:</h2>1. take notes here<br>')
        f.write('<hr><br>')
        f.write('<br><h2>Description:</h2>{}<br>'.format(
            meeting.meeting['description']
        ))
        f.write('<br><hr><br>')
        f.write('<br><b>Calendar link</b>:<br> {}<br><br>'.format(
            meeting.meeting['html_link']
        ))
        f.write('<b>Attendees</b>:<br><br>')
        att_build = 'Email | Status<br><br>'
        attendee_check = meeting.meeting['attendees']
        if attendee_check == 'No attendees':
            f.write(attendee_check)
        else:
            for attendee in meeting.meeting['attendees']:
                email = attendee.get('email')
                response_status = attendee.get('responseStatus')
                if 'resource' not in email:
                    att_build = att_build + '{} | {}<br>'.format(
                        email, response_status
                    )
            f.write(att_build)
        f.close()
        return file_path, file_name


def create_os_nuetral_filepath(filename, app_conf):
    home_dir = os.path.expanduser('~')
    meeting_dir = os.path.join(
        home_dir, 
        app_conf.configs['meeting_notes_folder'])
    meeting_path = os.path.join(meeting_dir, filename)
    return meeting_path


def check_for_client_secret(app_conf):
    home_dir = os.path.expanduser('~')
    client_secret_dir = os.path.join(
        home_dir,
        app_conf.configs['client_secret_file_location']
    )
    if not os.path.exists(client_secret_dir):
        os.makedirs(client_secret_dir)

    client_secret_file = os.path.join(
        client_secret_dir,
        app_conf.configs['client_secret_file_name']
    )
    if not os.path.exists(client_secret_file):
        cs_status = False
    else:
        cs_status = True
    return cs_status


def check_for_meeting_notes_folder(app_conf):
    home_dir = os.path.expanduser('~')
    meeting_notes_dir = os.path.join(
        home_dir,
        app_conf.configs['meeting_notes_folder']
    )
    if not os.path.exists(meeting_notes_dir):
        os.makedirs(meeting_notes_dir)


def open_file_to_edit(type_of_file, file_path, app_conf):
    if type_of_file == 'markdown':
        os.system('{} \'{}\''.format(
            app_conf.configs['editor_cli_command'],
            file_path
            )
        )
    if type_of_file == 'google':
        webbrowser.open('https://docs.google.com/document/d/{}'.format(
            file_path
        ))


def open_in_markdown_editor(app_conf):
    open_setting = app_conf.configs['open_markdown_editor']
    open_setting.lower()
    if open_setting == 'true':
        return True
    else:
        return False


def launch_readme_in_browser():
    webbrowser.open('https://github.com/daubejb/meet')
    sys.exit()
