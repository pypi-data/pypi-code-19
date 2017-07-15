"""
Main module for recoo application
"""
import click

from .tastedive import TasteDiveApi


@click.command()
@click.option('--query', prompt='Search for: ',
              help='Name of the Book, Movie, Song for which you want to find similar things.')
def cli(query):
    """
    Command line application to get recommendations
    for the books, movies and songs based on query
    """
    taste_dive_api = TasteDiveApi()
    print(taste_dive_api.print_recommendations(query))
