import os
import sys
import csv
import logging
import yaml
import simplekml

DEFAULT_ICON_IMAGE = 'https://maps.google.com/mapfiles/kml/paddle/red-circle.png'
DEFAULT_ICON_COLOR = 'ffffffff'
DEFAULT_ICON_SCALE = 1.0
DEFAULT_TEXT_SCALE = 1.0


def create_kmz_from_csv(csv_file: str, output_dir: str,
                        styles=None) -> str:
    """ Converts a parsed csv file to a kmz Google Earth overlay.

    :param csv_file: Filepath to csv input file
    :param output_dir: Specify alternate output directory for kmz
    :param styles: Specify additional style config
    :return: Filepath of outputted kmz file
    """

    if not os.path.isfile(csv_file):
        logging.error('The input file could not be found at %s', csv_file)
        return None

    styleSettings = load_styles(styles)

    # Create output folder if needed
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    h, data = import_csv_file(csv_file)
    pointData = convert_data(h, data)

    csv_dir, csv_name = os.path.split(csv_file)
    file_name = os.path.splitext(csv_name)[0]
    kmzFile = os.path.join(output_dir, '{}.kmz'.format(file_name))

    return export_overlay(kmzFile, pointData, styleSettings)


def load_styles(style_yaml) -> dict:
    """ Load point style dictionary """

    default_style = {"icon_image": DEFAULT_ICON_IMAGE,
                    "icon_color": DEFAULT_ICON_COLOR,
                    "icon_scale": DEFAULT_ICON_SCALE,
                    "text_scale": DEFAULT_TEXT_SCALE,
                    }
    styles = {'Default': default_style}

    if style_yaml is None:
        return styles

    if not os.path.isfile(style_yaml):
        logging.error('Invalid style file location %s', style_yaml)
        return styles

    with open(style_yaml, 'r') as stream:
        new_styles = yaml.load(stream)

    for style in new_styles:
        if style in styles:
            logging.warning('Style %s already exists', style)
            continue
        else:
            styles[style] = dict()  # Create new style
        
        for attr in ['icon_image', 'icon_color', 'icon_scale', 'text_scale']:
            if attr in new_styles[style]:
                attr_val = new_styles[style][attr]
            else:
                attr_val = default_style[attr]
            styles[style][attr] = attr_val
    return styles


def export_overlay(file_path, pnt_data: list, styles: dict):
    """ Build point objects then export
    """

    kml = simplekml.Kml()
    # Get list of unique folders
    folders = []
    for row in pnt_data:
        folder = row[0].strip()
        folders.append(folder)
    folders = list(set(folders))

    # Add points to corresponding folder
    for folder in sorted(folders):
        fol = kml.newfolder(name=folder)
        for point in pnt_data:
            pnt_folder = point[0]
            if pnt_folder == folder:
                lat = point[3]
                lon = point[2]
                coords = [(lat, lon)]
                pnt_name = point[1]
                pnt_desc = point[5]
                style_desc = point[4]

                # Don't add points without co-ordinates
                if lat and lon:
                    # Create the point
                    pnt = fol.newpoint(name=pnt_name, coords=coords,
                                       description=pnt_desc)
                    # Load styles
                    try:
                        style = styles[style_desc]
                    except KeyError:
                        msg = 'Style %s not specified'
                        logging.warning(msg, style_desc)
                        style = styles['Default']

                    # Apply styles
                    pnt.style.iconstyle.icon.href = style['icon_image']
                    pnt.style.iconstyle.color = style['icon_color']
                    pnt.style.iconstyle.scale = style['icon_scale']
                    pnt.style.labelstyle.scale = style['text_scale']

    # Save File as KMZ
    kml.savekmz(file_path)

    # simplekml doesn't let you open the class as a with
    # So flush output when finished to close object
    sys.stdout.flush()
    return file_path


def convert_data(h, data):
    """ Converts additional headings into HTML table
    """
    convData = []
    for row in data:
        newRow = process_data_row(h, row)
        convData.append(newRow)

    return convData


def process_data_row(h, row):
    """ Process a single row of data
    """
    try:
        folderName = str(row[0].strip())
        pointTitle = str(row[1].strip())
    except IndexError:
        logging.error('Data is not in the required format!')
        raise
    try:
        latitude = float(row[2].strip())
        longitude = float(row[3].strip())
    except ValueError:
        logging.warning(
            'Co-ordinates not in correct format for point ' + pointTitle)
        latitude, longitude = None, None
    style = str(row[4].strip())

    additionalCols = row[5:]
    cellHTML = create_html_table(h[5:], additionalCols)

    newRow = [folderName, pointTitle, latitude, longitude, style, cellHTML]

    return newRow


def create_html_table(headings, additionalCols):
    """ Convert any additional columns into a HTML table
    """
    cellHTML = ''
    for i, cell in enumerate(additionalCols):
        try:
            cellHTML += '<dt>' + headings[i].strip() + '</dt>'
        except:
            cellHTML += '<dt>Unknown Heading</dt>'
        cellHTML += '<dd>' + cell.strip() + '</dd>'
    return cellHTML


def import_csv_file(fPath):
    """ Import the csv rows as list objects
    """
    data = []
    with open(fPath, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        h = next(reader, None)  # first row is headings
        for row in reader:
            data.append(row)
    return h, data
