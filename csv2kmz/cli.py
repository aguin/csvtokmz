import logging
import click
from . import create_kmz_from_csv


@click.command()
@click.option('--csvfile', '-i', prompt='Input CSV File',
              help='The csv file to convert.')
@click.option('--output', '-o', default='',
              help='The output directory.')
@click.option('--styles', '-s', default=None,
              help='Specify location of settings for point styles')
def cli(csvfile, output, styles):
    """ CSVtoKMZ
    Converts a parsed csv file to a kmz Google Earth overlay.
    """

    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        level=logging.INFO)
    kmz = create_kmz_from_csv(csvfile, output, styles)
    logging.info('Created %s', kmz)


if __name__ == '__main__':
    cli()
