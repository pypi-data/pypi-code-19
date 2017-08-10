import click

from .processor import LogsProcessor
from .formatter import LogsFormatter
import yaml

@click.command()
@click.option('--format', '-f', type=click.Choice(['json', 'csv']), default='json')
@click.option('--logs-path', '-l', required=True)
@click.option('--out-path', '-o', required=True)
@click.option('--config-path', '-c', required=True)

def main(format, logs_path, out_path, config_path):
    config_file = open(config_path, 'r')
    config = yaml.load(config_file)
    processor = LogsProcessor(logs_path)
    formatter = LogsFormatter(out_path, format, config)
    formatter.run(processor)

if __name__ == '__main__':
    main()
