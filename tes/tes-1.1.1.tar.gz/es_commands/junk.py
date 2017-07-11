# @cat.command('aliases', short_help='Information about current aliases')
# @click.option('--name', nargs=1, help=name_column_help)
# @click.option('-h', nargs=1, help=h_column_help)
# def aliases(name,h):
#     '''aliases shows information about currently configured aliases to indices including filter and routing infos.'''
#     try:
#         response = base.es.cat.aliases(name,h=h)
#         if not response:
#             click.echo("No aliases as of now")
#             return
#         table = base.draw_table(response)
#     except Exception as e:
#         click.echo(e)
#     else:
#         click.echo(table.draw())


# @cat.command()
# @click.option('-h', nargs=1, help=h_column_help)
# def master(h):
#     try:
#         response = base.es.cat.master(h=h)
#         table = base.draw_table(response)
#     except Exception as e:
#         click.echo(e)
#     else:
#         click.echo(table.draw())


# @cat.command()
# @click.option('-h', nargs=1, help=h_column_help)
# def pending_tasks(h):
#     try:
#         response = base.es.cat.pending_tasks(h=h)
#         if not response:
#             click.echo("No Pending Tasks as of now")
#             return
#         table = base.draw_table(response)
#     except Exception as e:
#         click.echo(e)
#     else:
#         click.echo(table.draw())

# @cat.command()
# @click.option('-h', nargs=1, help=h_column_help)
# def plugins(h):
#     try:
#         response = base.es.cat.plugins(h=h)
#         if not response:
#             click.echo("No Plugins as of now")
#             return
#         table = base.draw_table(response)
#     except Exception as e:
#         click.echo(e)
#     else:
#         click.echo(table.draw())


# @cat.command()
# @click.option('--actions', nargs=1, help=action_column_help)
# @click.option('-h', nargs=1, help=h_column_help)
# @click.option('--node', nargs=1, help=node_column_help)
# @click.option('--detailed', is_flag=True, help=detailed_column_help)
# def tasks(actions,h, node, detailed):
#     try:
#         response = base.es.cat.tasks(actions=actions, h=h, node_id=node, detailed=detailed)
#         if not response:
#             click.echo("No tasks present")
#             return
#         table = base.draw_table(response)
#     except Exception as e:
#         click.echo(e)
#     else:
#         click.echo(table.draw())
