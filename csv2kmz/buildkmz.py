import os
import json
import csv
import sys
import logging
import simplekml


def create_kmz_from_csv(csvFile, styleFile='settings/styles.json', outputDir='output/'):
    """ Check file locations exists and then process
    """
    styleSettings = load_styles(os.path.abspath(styleFile))
    csvFile = os.path.abspath(csvFile)
    if not os.path.isfile(csvFile):
        logging.error('The input file could not be found at ' + str(csvFile))

    h, data = import_csv_file(csvFile)
    pointData = convert_data(h, data)

    # Specify output file location
    outputDir = os.path.abspath(outputDir)
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    csvDir, csvName = os.path.split(csvFile)
    fileName = os.path.splitext(csvName)[0]
    kmzFile = os.path.join(outputDir,fileName+'.kmz')


    return export_overlay(kmzFile, pointData, styleSettings)


def load_styles(styleFile):
    """ Load point style dictionary
    """
    if not os.path.isfile(styleFile):
        logging.error('The style settings could not be loaded from '+str(styleFile))

    with open(styleFile) as sf:
        try:
            styleSettings = json.load(sf)
        except ValueError:
            logging.error('The styles json file is not in the correct format!')
            raise
    return styleSettings


def export_overlay(fPath, pointData, styleSettings):
    """ Build point objects then export
    """

    kml = simplekml.Kml()

    # Get list of unique folders
    folders = []
    for row in pointData:
        folders.append(row[0].strip())
    folders = list(set(folders))

    # Add points to corresponding folder
    for folder in folders:
        fol = kml.newfolder(name=folder)
        for point in pointData:
            pntFolder = point[0]
            if pntFolder == folder:
                latlon = ((point[3]), (point[2]))
                pntName = point[1]
                pntDesc = point[5]

                # Don't add points without co-ordinates
                if not latlon == (None, None):
                    # Create the point
                    pnt = fol.newpoint(name=pntName, coords=[latlon],
                                       description=pntDesc)

                    # Load styles
                    try:
                        style = styleSettings[point[4]]
                    except KeyError:
                        logging.warning('Style '+ str(point[4]) + ' not found.')
                        # Specify default style
                        try:
                            style = styleSettings['Default']
                        except KeyError:
                            logging.error('No default style specified')
                            style = {'textScale': None,
                                     'iconColor': None,
                                     'iconScale': None,
                                     'iconImage': None}

                    # Apply styles
                    try:
                        pnt.style.labelstyle.scale = style['textScale']
                        pnt.style.iconstyle.color = style['iconColor']
                        pnt.style.iconstyle.scale = style['iconScale']
                        pnt.style.iconstyle.icon.href = style['iconImage']
                    except KeyError:
                        logging.error('The styles json is not in the correct format!')

    # Save File as KMZ
    kml.savekmz(fPath)
    sys.stdout.flush()

    return fPath


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
        logging.warning('Co-ordinates not in correct format for point '+pointTitle)
        latitude, longitude = None, None
    style = str(row[4].strip())

    additionalCols = row[4:]
    cellHTML = create_html_table(h, additionalCols)

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
