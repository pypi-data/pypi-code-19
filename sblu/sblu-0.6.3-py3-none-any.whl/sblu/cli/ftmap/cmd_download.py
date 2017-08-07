import logging
import click
import requests
import json
import sys

from sblu import CONFIG
from sblu.cli import make_sig

logger = logging.getLogger(__name__)

URL_SCHEME = "http"
API_ENDPOINT = "/api_download.php"
CP_CONFIG = CONFIG['ftmap']
FORM_KEYS = (
    'username', 'secret', 'jobid', 'filetype'
)
FILETYPE_CHOICES = (
    'user_prot_file', '1sidems_file', 'prot_psf', 'user_prot_img',
    'proc_prot_file', 'proc_prot_img', 'model_bz2', 'model_file',
    'model_pse', 'modelb64pse', 'nb_file', 'hb_file', 'summary_file',
    'ftsite_zip', 'ftflex_zip', 'contacts_zip', 'ftdyn_zip'
)

@click.command('download', short_help="Download jobs from FTMap.")
@click.option("--username", default=CP_CONFIG['username'])
@click.option("--secret", default=CP_CONFIG['api_secret'])
@click.option("--server", default=CP_CONFIG['server'])
@click.option("--filetype", default=None, type=click.Choice(FILETYPE_CHOICES))
@click.argument("jobids", nargs=-1, required=True)
def cli(username, secret, server, filetype,
        jobids):
    if username is None or username == "None" or secret is None or secret == "None":
        if username is None or username == "None":
            username = click.prompt("Please enter your ftmap username")
            CP_CONFIG['username'] = username
        if secret is None or secret == "None":
            secret = click.prompt("Please enter your ftmap api secret")
            CP_CONFIG['api_secret'] = secret
        CONFIG.write()

    api_address = "{0}://{1}{2}".format(URL_SCHEME, server, API_ENDPOINT)
    for jobid in jobids:
        form = {
            k: v for k, v in locals().items() if k in FORM_KEYS and v is not None
        }

        form['sig'] = make_sig(form, secret)
        print(form)

        try:
            print("Downloading {}...".format(jobid), end="", file=sys.stderr)
            r = requests.post(api_address, data=form)

            if r.status_code != requests.codes.ok:
                print("ERROR", file=sys.stderr)
                for e in json.loads(r.text)['errors']:
                    print(e, file=sys.stderr)
                continue
            else:
                with open("ftmap.{}.tar.bz2".format(jobid), "wb") as out:
                    out.write(r.content)
            print("OK", file=sys.stderr)
        except:
            logger.error("Error downloading job {}".format(jobid))
