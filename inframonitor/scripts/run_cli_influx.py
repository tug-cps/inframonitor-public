import click

from common.dbwrapper import InfluxDBWrapper

db_wrapper = InfluxDBWrapper('localhost', 'mqtt', 'sensor-readings')


@click.group()
def cli():
    """
    Command line tool for time series database\n
    can be used to read and update time series entries
    """
    pass


@cli.command('get')
@click.argument('sensor')
@click.argument('look_back')
def get(sensor, look_back):
    """
    get entries for a sensor, use look_back to specify the time horizon, e.g. 3h or 2d
    """
    response = db_wrapper.get(sensor, look_back)
    print(response)


if __name__ == '__main__':
    cli()
