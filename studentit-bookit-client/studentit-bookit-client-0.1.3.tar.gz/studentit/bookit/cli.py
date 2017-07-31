import traceback

import click

from studentit.bookit.api.api_client import ApiClient


@click.group()
@click.option('--username')
@click.option('--password')
@click.pass_context
def cli(ctx, username, password):
    ctx.obj = ApiClient(username, password)


@cli.group()
def server():
    pass


@cli.group()
def admin():
    pass


@cli.group()
def site():
    pass


@cli.group()
def resource():
    pass


@cli.group()
def booking():
    pass


@booking.command()
@click.argument('start_time')
@click.argument('end_time')
@click.argument('booking_date')
@click.argument('resource_id')
@click.option('--email-receipt', required=True, default=False)
@click.pass_obj
def create(client, start_time, end_time, booking_date, resource_id, email_receipt):
    print(client.create_booking(start_time, end_time, booking_date, resource_id, email_receipt))


@booking.command()
@click.argument('booking_id')
@click.option('--email-receipt', required=True, default=False)
@click.pass_obj
def delete(client, booking_id, email_receipt):
    print(client.delete_booking(booking_id, email_receipt))


@booking.command()
@click.pass_obj
def list(client):
    print(client.list_bookings())


@site.command(name='status')
@click.option('--site-id')
@click.pass_obj
def site_resource_status(client, site_id):
    print(client.all_resource_status(site_id=site_id))


@server.command(name='status')
@click.pass_obj
def server_status(client):
    if client.server_status():
        print('BookIT is up and responding to requests')
    else:
        print('BookIT is down')


@admin.command(name='all-resource-status')
@click.option('--site-id')
@click.pass_obj
def admin_all_resource_status(client, site_id):
    print(client.admin_all_resource_status(site_id))


@admin.command(name='location-status')
@click.option('--location-id', required=True)
@click.pass_obj
def admin_location_status(client, location_id):
    print(client.admin_location_status(location_id))


def main():
    try:
        cli(auto_envvar_prefix='BOOKIT')
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_exc()


if __name__ == '__main__':
    main()
