import unittest
import os
from csv2kmz import create_kmz_from_csv


class TestKMZBuilds(unittest.TestCase):

    def test_working_example(self):
        """ Should complete with no errors
        """
        styleFile = '../../settings/styles.json'
        outputDir = 'output/'

        csvFile = 'data/Example1.csv'
        kmz = create_kmz_from_csv(csvFile,styleFile,outputDir)
        self.assertEqual(os.path.split(kmz)[1], 'Example1.kmz')

    def test_example_with_warnings(self):
        """ Should complete with warnings but no errors
        """
        styleFile = '../../settings/styles.json'
        outputDir = 'output/'

        csvFile = 'data/Example2.csv'
        kmz = create_kmz_from_csv(csvFile, styleFile, outputDir)
        self.assertEqual(os.path.split(kmz)[1], 'Example2.kmz')


    def test_broken_example(self):
        """ Should raise an error as not in the right format
        """
        styleFile = '../../settings/styles.json'
        outputDir = 'output/'

        csvFile = 'data/Example-Errors.csv'

        self.assertRaises(IndexError, create_kmz_from_csv, csvFile, styleFile, outputDir)


if __name__ == '__main__':
    unittest.main()