# -*- coding: utf-8 -*-
import click
import datetime

from constants import ShowInfo, TaskStatus
from colourful import Colour, cprint
from file_handler import read_file, write_file


def not_completed_todos():
    todos = read_file()
    return sorted([todo for todo in todos if todo['status'] == TaskStatus.DOING], key=lambda x:x['created_time'])


def completed_todos():
    todos = read_file()
    return sorted([todo for todo in todos if todo['status'] == TaskStatus.DONE], key=lambda x:x['created_time'])


def show(show_info_type=None):
    if show_info_type == ShowInfo.ADDED:
        cprint('Task is added, my lord.', Colour.GREEN)
    elif show_info_type == ShowInfo.EXIST:
        cprint('Task already exists, my lord', Colour.GREEN)
    elif show_info_type == ShowInfo.DOING:
        for index, todo in enumerate(not_completed_todos()):
            cprint('{}. {}'.format(index+1, unicode(todo['task_detail']).encode('utf-8')), Colour.RED)
    elif show_info_type == ShowInfo.DONE:
        for index, todo in enumerate(completed_todos()):
            cprint('{}. {}'.format(index+1, todo['task_detail'].encode('utf-8')), Colour.GREEN)
    elif show_info_type == ShowInfo.ALL:
        show(ShowInfo.DOING)
        show(ShowInfo.DONE)


@click.command()
@click.argument('task_detail')
def add(task_detail):
    todos = read_file()
    if task_detail in [unicode(t['task_detail']) for t in todos]:
        show(ShowInfo.EXIST)
    else:
        todos.append(
            {
                'task_detail': task_detail,
                'status': TaskStatus.DOING,
                'created_time': datetime.datetime.now(),
                'updated_time': datetime.datetime.now()
            }
        )
        write_file(todos)
        show(ShowInfo.ADDED)
    show(ShowInfo.DOING)
    show(ShowInfo.DONE)


@click.command()
def _list():
    show(ShowInfo.ALL)


@click.command()
@click.argument('task_id')
def kill(task_id):
    todos = not_completed_todos()
    todos[int(task_id)-1]['status'] = 1
    write_file(todos + completed_todos())
    show(ShowInfo.ALL)
