#!/usr/bin/env python
import flickr_api
import sys, os, errno, syslog, argparse
import time
import datetime as dt
import yaml

ONEHOUR = 3600

def main():
    # default config file path setup
    # use this if the user does not use the -f option to provide file path
    default_configfile = "{}/.flickr_archiver/config.yaml".format(os.path.expanduser('~'))

    # let the user provide a different path other than the default to the
    # -f option
    parser = argparse.ArgumentParser(
        description='Two optional arguments, -f, for config file path.'
                    ' or -e for an example config file'
    )
    parser.add_argument(
        '-t', dest='template', action='store_true',
        help='Use this to generate a template to stdout',
        required=False
    )
    parser.add_argument(
        '-f', dest='configfile', metavar='<config path>',
        help='Optionally provide the config file path',
        required=False
    )

    # get the arguments into args object
    args = parser.parse_args()

    # first take care of the -e argument (show example template)
    if args.template:
        # givem what they ask for
        print("Here is a config file template:\n"
              "api_sec: <figure this out yourself>\n"
              "api_key: <figure this out yourself>\n"
              "base_folder: <for storing your items>\n"
              "min_upload_hours: <how far to go back in hours>\n"
              "per_page: <output is paginated so, how many per page?>\n"
              "auth_file: <path to your auth file>")

        # exit plox
        sys.exit(0)

    # use either a provided config file path or the default
    if args.configfile and os.path.isfile(args.configfile):
        run(configpath=args.configfile)
    elif os.path.isfile(default_configfile):
        run(configpath=default_configfile)
    else:
        raise Exception("You must provide a config file path, either "
                        "with the -f option or in ~/.flickr_archiver")


def run(configpath=None):

    configfile = file(configpath)
    config = yaml.load(configfile)

    # make folders automatically
    def mkdir_p(path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    # load api keys
    api_sec=config['api_sec']
    api_key=config['api_key']
    per_page=config['per_page']
    min_upload_date=time.time() - (config['min_upload_hours'] * ONEHOUR)
    base_folder=config['base_folder'].rstrip('/')

    # set the api keys to use
    flickr_api.set_keys(api_key=api_key, api_secret=api_sec)

    # load stored auth file
    flickr_api.set_auth_handler(config['auth_file'])

    # due to the auth above, flickr_api assumes your username
    # so the next line is not needed
    # this should log you in
    me = flickr_api.test.login()
    # with the login this should work

    # getPhotos returns a special "list" that has an info object attached
    # the info object has the total pages, current page and number of pages
    # we need to go through all the pages so we need the .pages attribute
    info = me.getPhotos(min_upload_date=min_upload_date, per_page=per_page).info
    syslog.syslog(syslog.LOG_WARNING, "Info is {}".format(info))

    # pages starts with fucking 1 of course so adjusting...
    pages = [a+1 for a in range(info.pages)]
    syslog.syslog(syslog.LOG_WARNING, "There are {} pages".format(len(pages)))

    # loop through each page and re"get" the photos list object for the current page
    for i in pages:
        # show which page we are on
        syslog.syslog(syslog.LOG_WARNING, "on page {}".format(i))

        # get the new photos list object for the current page
        pics = me.getPhotos(min_upload_date=min_upload_date, per_page=per_page, page=i)

        syslog.syslog(syslog.LOG_WARNING, "There are {} items on this page".format(len(pics)))
        # loop through each photo in the list
        for pic in pics:
            # just get the year/month/day
            taken = pic.taken.split()[0]
            year,month,day = taken.split('-')
            folderpath = base_folder + "/{}/{}/{}".format(year,month,day)
            mkdir_p(folderpath)
            filepath = "{}/{}-{}-{}_{}".format(folderpath, year,month,day,pic.id)
            if pic.media == 'photo':
                filepath = "{}.{}".format(filepath,"jpg")
                if os.path.exists(filepath):
                    syslog.syslog(syslog.LOG_WARNING, "Skipping file {} since we already have it".format(filepath))
                    continue
                try:
                    syslog.syslog(syslog.LOG_WARNING, "    saving {} to {}".format(pic.id, filepath))
                    pic.save(filepath, size_label='Original')
                except Exception as e:
                    syslog.syslog(syslog.LOG_WARNING, "Got exception: {} for path {}".format(str(e), filepath))
            elif pic.media == 'video':
                filepath = "{}.{}".format(filepath,"mp4")
                if os.path.exists(filepath):
                    syslog.syslog(syslog.LOG_WARNING, "Skipping file {} since we already have it".format(filepath))
                    continue
                try:
                    syslog.syslog(syslog.LOG_WARNING, "    saving {} to {}".format(pic.id, filepath))
                    pic.save(filepath)
                except Exception as e:
                    syslog.syslog(syslog.LOG_WARNING, "Got exception: {} for path {}".format(str(e), filepath))
            else:
                syslog.syslog(syslog.LOG_WARNING, "wtf. id is {}, type is {}".format(pic.id, pic.media))

if __name__ == '__main__':
    main()
