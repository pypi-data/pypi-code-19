#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import gantt
import click
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


@click.command()
@click.option('--start', default=datetime.date.today(), help='Start date for sprint plan', prompt=True)
@click.option('--sprints', default=10, help='Number of sprints in plan.', prompt=True)
@click.option('--duration', default=10, help='Sprint duration in days.', prompt=True)
@click.option('--name', default="Project Clitheroe", help='Project name.', prompt=True)
def create_gant(start, sprints, duration, name):
    # Change font default
    gantt.define_font_attributes(fill='white', stroke='white', stroke_width=1,
                                 font_family="Ubuntu")

    p1 = gantt.Project(name=name)

    if not isinstance(start, datetime.date):
        start_date = parse(start)
    else:
        start_date = start

    end_date = start_date + relativedelta(days=(duration + 2) * sprints)
    print(start_date, end_date)
    curr_t = None
    # Create some tasks
    for sprint in range(sprints):
        t = gantt.Task(name=f'Sprint {sprint}', start=start_date,
                        duration=10, percent_done=44, color="#0000FF",
                        depends_of=curr_t)
        curr_t = t
        p1.add_task(t)

    p1.make_svg_for_tasks(filename='test_full.svg', today=datetime.date.today(),
                          start=start_date,
                          end=end_date)

if __name__ == '__main__':
    create_gant()
