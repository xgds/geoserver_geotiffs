from time import sleep
from requests import put, post, get
from requests.auth import HTTPBasicAuth
from string import ascii_lowercase, digits
from random import choice
from pprint import pprint
from shutil import copyfileobj


def random_string_generator(N):
    return ''.join(choice(ascii_lowercase + digits) for _ in range(N))


def create_wms_request(json):
    llbb = json["coverage"]["latLonBoundingBox"]
    bbox = [
        llbb["minx"],
        llbb["miny"],
        llbb["maxx"],
        llbb["maxy"],
    ]
    bbox = ",".join([str(float(x)) for x in bbox])
    srs = llbb["crs"]
    layers = json["coverage"]["namespace"]["name"] + ":" + json["coverage"]["name"]
    return {
        'service': 'WMS',
        'version': '1.1.0',
        'request': 'GetMap',
        'layers': layers,
        'styles': '',
        'bbox': bbox,
        'width': '341',
        'height': '768',
        'srs': srs,
        'format': 'image/png',
    }

def upload_geotiff(file_handle):
    geoserver_authentication = HTTPBasicAuth(
        "admin",
        "geoserver",
    )
    geoserverURL  = "http://geoserver:8080/geoserver/" 
    workspaceName = random_string_generator(10)
    storeName     = random_string_generator(10)

    # -----------------------------------------------------------
    # this example will create a new workspace each time; you should not
    # do this in practice though
    # -----------------------------------------------------------
    url = geoserverURL + "rest/workspaces.xml"
    r = post(
        url=url,
        auth=geoserver_authentication,
        headers={
            "Content-type": "application/xml"
        },
        data="<workspace><name>" + workspaceName + "</name></workspace>"
    )
    assert r.status_code == 201, r.status_code

    # -----------------------------------------------------------
    # if you get a 500 status code from this PUT request then you probably sent a bad GeoTIFF (not georeferenced)
    # see: http://osgeo-org.1560.x6.nabble.com/Unable-to-publish-GeoTiff-images-on-GeoServer-td4558056.html
    # -----------------------------------------------------------
    url = geoserverURL + "rest/workspaces/" + workspaceName + "/coveragestores/" + \
          storeName + "/file.geotiff?configure=all";
    data = file_handle.read()
    r = put(
        url=url,
        auth=geoserver_authentication,
        headers={
            'Content-type': 'image/tiff',
        },
        data=data,
    )
    assert r.status_code < 300, r.status_code

    json_url = geoserverURL + "rest/layers/" + \
               workspaceName + ":" + storeName + ".json"
    r = get(
        url=json_url,
        auth=geoserver_authentication,
    )
    assert r.status_code < 300, r.status_code
    
    coverage = r.json()["layer"]["resource"]["href"]
    r = get(
        url=coverage,
        auth=geoserver_authentication,
    )
    assert r.status_code < 300, r.status_code
    
    wms_json = r.json()
    url = geoserverURL + workspaceName + "/wms"
    r = get(
        url=url,
        params=create_wms_request(wms_json),
        auth=geoserver_authentication,
        stream=True,
    )
    assert r.status_code < 300, r.status_code

    with open("/geotiffs/output_" + storeName + ".png", 'wb') as f:
        r.raw.decode_content = True
        copyfileobj(r.raw, f)


if __name__ == "__main__":
    sleep(10)
    with open("/geotiffs/NA087_20170907_Heceta_North_5m_img.tif", 'rb') as f:
        upload_geotiff(f)

