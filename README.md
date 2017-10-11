# csvtokmz
Converts CSV files in a specified format into a KMZ overlay.

CSV Files should be in the format:
```
Folder Name, Point Title, Latitude, Longitude, Point Style, Detail 1, Detail 2, etc.
```

The csv can then be converted with the following command
```shell
python3 -m csv2kmz -i examples/Example2.csv -s examples/example-styles.yaml
```


