import os
import argparse
from buildkmz import create_kmz_from_csv
        
def main():
    """ Build file as per user inputs
    """
    
    args = get_cmd_args() 
    iPath = args.input
    sPath = args.styles
    oDir = args.output
    create_kmz_from_csv(iPath,sPath,oDir)
    

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
                        default='../output/')
    parser.add_argument('-s','--styles', help='Specify location of settings for point styles', 
                        default='settings/styles.json')   
    parser.add_argument('-i','--input', help='Specify file to convert', 
                        default='data/Example.csv')                         
    return parser.parse_args()    
    
if __name__ == '__main__':
    main()


