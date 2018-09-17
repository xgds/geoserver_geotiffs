## Geoserver GeoTIFF uploader

This repository is meant to serve as a sample case of uploading a GeoTIFF to Geoserver through a simple Python function and then downloading a WMS tile as a PNG file to demonstrate that the GeoTIFF was uploaded successfully.

The bulk of the work of this repository can be found in the file `python-tests/geotiffs.py`.

To start the example, make sure you have a folder called `geotiffs` and inside it have a GeoTIFF file. Then you can use the commands below.

```
docker-compose build
docker-compose up
```

