#!/usr/bin/env python3

from __future__ import print_function
import os
import json
import argparse
import csv
import sys

import simplekml


        
def convert_data(h,data):
    """ Converts additional headings into HTML table
    """ 
    
    num_headings = len(h)
    convData = []
    for row in data:
        newRow = []
        newRow.append(row[0]) # Folder Name
        newRow.append(row[1]) # Point Title
        newRow.append(row[2]) # Latitude
        newRow.append(row[3]) # Longitude
        newRow.append(row[4]) # Style
            
        cellHTML = ''
        for i, cell in enumerate(row):
            if i > 4:
                try:
                    cellHTML += '<dt>' + h[i] + '</dt>'
                except:
                    cellHTML += '<dt>Unknown Heading</dt>'
                cellHTML += '<dd>' + cell + '</dd>'
        newRow.append(cellHTML)
        convData.append(newRow)
    
    return convData

    
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
    
def export_overlay(fPath, pointData, styleSettings):
    """ Build point objects then export
    """

    # Generate new KML object
    kml = simplekml.Kml()

    # Get list of unique folders
    folders = []
    for row in pointData:
        folders.append(row[0].strip())
    folders = list(set(folders))

    # Add points tocorresponding folder
    for folder in folders:
        fol = kml.newfolder(name=folder)
        for point in pointData:
            pntFolder = point[0].strip()
            if pntFolder == folder:
                latlon = (float(point[2]),float(point[3]))
                pntName = point[1].strip()
                pntDesc = point[5].strip()
                style = styleSettings[point[4].strip()]

                pnt = fol.newpoint(name=pntName, coords=[latlon], description=pntDesc)
                pnt.style.labelstyle.scale = style['textScale']
                pnt.style.iconstyle.color = style['iconColor']
                pnt.style.iconstyle.scale = style['iconScale']
                pnt.style.iconstyle.icon.href = style['iconImage']

    # Save File as KMZ
    kml.savekmz(fPath)
    sys.stdout.flush()

def main():
    """ Main function
    """
    
    args = get_cmd_args() 

    outputDir = args.output       
    fPath = os.path.abspath(args.input)
    h, d = import_csv_file(fPath)

    pointData = convert_data(h,d)

    style = os.path.abspath(args.styles)
    with open(style) as sf:
        styleSettings = json.load(sf)

    outputPath = 'test.kmz'
    fPath = export_overlay(outputPath, pointData, styleSettings)



def get_cmd_args():
    """Get, process and return command line arguments to the script
    """    
    help_description = '''
CSVtoKMZ

Converts a parsed .csv file to a .kmz Google Earth overlay.
'''
    help_epilog = ''
    parser = argparse.ArgumentParser(description=help_description,
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=help_epilog)
    parser.add_argument('-o','--output', help='Specify alternate output directory', 
                        default='output/')
    parser.add_argument('-s','--styles', help='Specify location of settings for point styles', 
                        default='settings/styles.json')   
    parser.add_argument('-i','--input', help='Specify file to convert', 
                        default='data/Example.csv')                         
    return parser.parse_args()    
    
if __name__ == '__main__':
    main()


