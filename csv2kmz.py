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
        newRow.append(row[0].strip()) # Folder Name
        newRow.append(row[1].strip()) # Point Title
        try:
            newRow.append(float(row[2].strip())) # Latitude
            newRow.append(float(row[3].strip())) # Longitude
        except ValueError: # Not a Valid Number
            print('WARNING: Co-ordinates not in correct format for point',row[1].strip())
            newRow.append(None) 
            newRow.append(None)
            
        newRow.append(row[4].strip()) # Style
            
        cellHTML = ''
        for i, cell in enumerate(row):
            if i > 4:
                try:
                    cellHTML += '<dt>' + h[i].strip() + '</dt>'
                except:
                    cellHTML += '<dt>Unknown Heading</dt>'
                cellHTML += '<dd>' + cell.strip() + '</dd>'
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
            pntFolder = point[0]
            if pntFolder == folder:
                latlon = ((point[3]),(point[2]))
                pntName = point[1]
                pntDesc = point[5]

                if not latlon == (None, None): # Don't add points without co-ordinates
                    # Create the point
                    pnt = fol.newpoint(name=pntName, coords=[latlon], description=pntDesc)
                    
                    # Load styles
                    try:
                        style = styleSettings[point[4]]
                    except KeyError:
                        print('WARNING: Style','"'+point[4]+'"','not found.')
                        # Specify default style
                        try:
                            style = styleSettings['Default']
                        except KeyError:
                            print('ERROR: No default style specified')
                            style = {'textScale':None,
                                     'iconColor':None,
                                     'iconScale':None, 
                                     'iconImage':None}
                            
                    # Apply styles
                    try:
                        pnt.style.labelstyle.scale = style['textScale']
                        pnt.style.iconstyle.color = style['iconColor']
                        pnt.style.iconstyle.scale = style['iconScale']
                        pnt.style.iconstyle.icon.href = style['iconImage']
                    except KeyError:
                        print('ERROR: The styles json is not in the correct format!')
                
    # Save File as KMZ
    kml.savekmz(fPath)
    sys.stdout.flush()

    return fPath
    
def create_directory(fDir):
    """ Checks if a directory exists, and creates it it does not
    """
    try:
        os.makedirs(fDir)
    except OSError:
        pass

        
def main():
    """ Main function
    """
    
    args = get_cmd_args() 
    iPath = os.path.abspath(args.input)
    sPath = os.path.abspath(args.styles)
    oDir = os.path.abspath(args.output)
    success = process_file(iPath,sPath,oDir)
    
    
def process_file(iPath,sPath,oDir):
    """ Check file locations exists and then process
    """
    
    # Load point style dictionary
    try:
        with open(sPath) as sf:
            try:
                styleSettings = json.load(sf)
            except ValueError: 
                print('ERROR: The styles json file is not in the correct format!')
                return False
    except FileNotFoundError:
        print('ERROR: The specified style file:')
        print('',sPath)
        print('','was not found!')
        return False
        
    # Load in the input data
    try:
        h, d = import_csv_file(iPath)
        try:
            pointData = convert_data(h,d)
        except IndexError:
            print('ERROR: The specified csv input file is not in the correct format.')
            return False
    except FileNotFoundError:
        print('ERROR: The specified input file:')
        print('',iPath)
        print('','was not found!')
        return False

    # Specify output file path
    create_directory(oDir)
    iDir, iFile = os.path.split(iPath)
    oFile = iFile.replace(".csv", "")   
    oPath = os.path.join(oDir,oFile+'.kmz')
    
    # Build the overlay
    fPath = export_overlay(oPath, pointData, styleSettings)
    print(fPath,'Created!')
    
    return True



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


