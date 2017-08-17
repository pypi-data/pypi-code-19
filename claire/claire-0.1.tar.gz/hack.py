import click
from clarifai import rest
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage
import validators
import requests
import os
import json
from pprint import pprint

app = ClarifaiApp()

@click.group()
def cli1():
    pass

@cli1.command()
@click.argument('ipath', required=True)
def predict(ipath):
    """ Calls and prints Clarifai's predict command against a URI"""
    model = app.models.get("general-v1.3")

    if validators.url(ipath):
        image = ClImage(ipath)
        jsonTags = model.predict([image])
        for tag in jsonTags['outputs'][0]['data']['concepts']:
            click.echo(tag['name'])
    elif os.path.exists(ipath):
        image = ClImage(file_obj=open(ipath, 'rb'))
        jsonTags = model.predict([image])
        for tag in jsonTags['outputs'][0]['data']['concepts']:
            click.echo(tag['name'])
    else:
        click.echo("you need to provide a valid url or local image path for the predict command")


@click.group()
def cli2():
    pass

@cli2.command()
@click.argument('path', type=click.Path(exists=True), required=True)
def upload(path):
    """Uploads all the images in a specified file path"""
    #app.inputs.create_image_from_filename(fname)
    for filename in os.listdir(path):
         if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith("jpg"):
             app.inputs.create_image_from_filename(path+"/"+filename)



cli = click.CommandCollection(sources=[cli1, cli2])

if __name__ == '__main__':
    cli()
