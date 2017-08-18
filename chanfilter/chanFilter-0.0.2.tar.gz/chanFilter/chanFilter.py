#!/usr/bin/python
import click
import requests
def findWord(w,s):
	return (' ' + w + ' ') in (' ' + s + ' ')
@click.command()
@click.option('-l','--list', is_flag=True, help='List all boards (overrides other options)')
@click.option('-b','--board', default='g', help='Board to search')
@click.option('-t','--text', 
		default='this random arbitrary string no single person will use unless they look at the source',
		help='Text to search')
@click.option('-i','--intelligent', is_flag=True, help='Searches via keywords and not just the string you entered')
def filter(list, board, text, intelligent):
	"""Tool to search BOARD for TEXT in the title or OP's post."""
	if list:
		boards = requests.get("http://a.4cdn.org/boards.json").json()
		for board in boards['boards']:
			click.echo(board['board'] + " - " + board['title'])
	else:
		if text == 'this random arbitrary string no single person will use unless they look at the source':
			raise Exception("Text not set")
		else:
			text = text.lower()
			catalog = requests.get("http://a.4cdn.org/" + board + "/catalog.json").json()
			if intelligent:
				text = text.split(" ")
				for page in catalog:
					for thread in page['threads']:
						sub = 'sub' in thread
						com = 'com' in thread
						for key in text:
							if sub:
								if findWord(key,thread['sub'].lower()):
									click.echo("https://boards.4chan.org/" + board + "/thread/" + str(thread['no']))
									break
							if com:
								if findWord(key,thread['com'].lower()):
									click.echo("https://boards.4chan.org/" + board + "/thread/" + str(thread['no']))
									break
			else:
				for page in catalog:
					for thread in page['threads']:
						if 'sub' in thread:
							if text in thread['sub'].lower():
								click.echo("https://boards.4chan.org/" + board + "/thread/" + str(thread['no']))
								continue
						if 'com' in thread:
							if text in thread['com'].lower():
								click.echo("https://boards.4chan.org/" + board + "/thread/" + str(thread['no']))
								continue
if __name__ == '__main__':
	filter()