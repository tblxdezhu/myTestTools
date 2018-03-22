#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 23/02/2018 1:18 PM
# @Author  : Zhenxuan Xu
# @Site    : 
# @File    : kml2data.py
# @Software: PyCharm

import sys
import os
import re


class Trajectory:
    def __init__(self, case, kml_name, fill_data, data_type, is_show=True):
        self.is_show = is_show
        self.name = ''.join(re.findall('[a-zA-Z0-9]+', kml_name + case))
        self.var_name = "co_" + self.name
        self.prefix = "var coordinates = [".replace("coordinates", self.var_name)
        self.suffix = "];"
        self.data = fill_data
        self.data_processed = []
        self.data_type = data_type
        self.string = '''
                    var name = new google.maps.Polyline({
                      path: coordinates,
                      geodesic: true,
                      strokeColor: '#FF0000',
                      strokeOpacity: 1.0,
                      strokeWeight: 2
                    });           
                    name.setMap(map);
                    '''.replace("name", self.name).replace("coordinates", self.var_name)
        self.write_info = ""

    def string_builder(self):
        for point in self.data:
            list_str = ['{lat:', str(point[1]), ',', 'lng:', str(point[0]), '},']
            self.data_processed.append(' '.join(list_str))
        if self.data_type == 'gps':
            self.string = self.string.replace("'#FF0000'", "'#00FF00'")
        self.write_info = ' '.join([self.prefix, ' '.join(self.data_processed), self.suffix, self.string])
        if self.is_show:
            return self.write_info
        else:
            return ""


def kml2coordinates(file_path):
    with open(file_path) as f:
        lines = f.readlines()
    coordinates = []
    for line in lines:
        if line.strip().startswith('<'):
            continue
        try:
            for coordinate in line.strip().split():
                lon, lat, alt = coordinate.split(',')
                coordinates.append((float(lon), float(lat)))
        except Exception, e:
            print "converting gps wrongly !!!"
            print e
            continue
    return coordinates


def get_all_kmls(path):
    data_set = {}
    tmp = ''
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith("hq_slam.kml") or file.endswith("process_gps.kml"):
                if os.path.basename(root) == "segment":
                    case_name = os.path.dirname(root).split('/')[-3] + "_" + os.path.basename(os.path.dirname(root))
                    if not case_name == tmp:
                        data_set[case_name] = []
                    data_set[case_name].append(os.path.join(root, file))
                    tmp = case_name
    return data_set


def data_process():
    data = {}
    center = {}
    for k, v in get_all_kmls(folder_path).items():
        data[k] = {}
        for kml in v:
            kml_type = 'slam'
            is_show = True
            kml_name = os.path.basename(kml)
            coordinate = kml2coordinates(kml)
            if 'gps' in kml_name:
                kml_type = 'gps'
                is_show = False
            trajectory = Trajectory(k, kml_name, coordinate, kml_type, is_show)
            data[k][trajectory.name] = trajectory.string_builder()
            center[k] = trajectory.data_processed[0]
    return data, center


def draw(mode):
    data, center_data = data_process()
    backup_path = os.path.join(sys.path[0], "webkmls")
    if os.path.exists(backup_path):
        os.system("rm -rf " + backup_path + "/*")
    else:
        os.system("mkdir " + backup_path)
    allinone_path = os.path.join(sys.path[0], "webkmls", mode+"_all_in.html")
    with open(allinone_path, 'w') as f:
        f.write(
            '''
            <!DOCTYPE html>
                <html>
                  <head>
                    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
                    <meta charset="utf-8">
                    <title>Trajectory Online</title>
                    <style>
                      /* Always set the map height explicitly to define the size of the div
                       * element that contains the map. */
                      #map {
                        height: 100%;
                      }
                      /* Optional: Makes the sample page fill the window. */
                      html, body {
                        height: 100%;
                        margin: 0;
                        padding: 0;
                      }
                    </style>
                  </head>
                  <body>
                    <div id="map"></div>
                    <script>
                      function initMap() {
                        var map = new google.maps.Map(document.getElementById('map'), {
                          zoom: 12,
                          center: 
            '''
        )
        f.write(center_data[center_data.keys()[0]])
        f.write(
            '''
                mapTypeId: 'terrain'
                });
            '''
        )
        for k in get_all_kmls(folder_path):
            for key in sorted(data[k].keys()):
                f.write(data[k][key])
        f.write(
            '''
                  }
                </script>
                <script async defer
                src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCrCqQQu48EaqNTTQQPNhzqJG4engiExkw&callback=initMap">
                </script>
              </body>
            </html>
            '''
        )
    for k in get_all_kmls(folder_path):
        path = os.path.join(sys.path[0], "webkmls", k + ".html")
        with open(path, 'w') as f:
            f.write(
                '''
                <!DOCTYPE html>
                <html>
                  <head>
                    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
                    <meta charset="utf-8">
                    <title>Trajectory Online</title>
                    <style>
                      /* Always set the map height explicitly to define the size of the div
                       * element that contains the map. */
                      #map {
                        height: 100%;
                      }
                      /* Optional: Makes the sample page fill the window. */
                      html, body {
                        height: 100%;
                        margin: 0;
                        padding: 0;
                      }
                    </style>
                  </head>
                  <body>
                    <div id="map"></div>
                    <script>
                      function initMap() {
                        var map = new google.maps.Map(document.getElementById('map'), {
                          zoom: 12,
                          center: 
                '''
            )
            f.write(center_data[k])
            f.write(
                '''
                    mapTypeId: 'terrain'
                        });
                '''
            )
            for key in sorted(data[k].keys()):
                f.write(data[k][key])
            f.write(
                '''
                      }
                    </script>
                    <script async defer
                    src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCrCqQQu48EaqNTTQQPNhzqJG4engiExkw&callback=initMap">
                    </script>
                  </body>
                </html>
                '''
            )


if __name__ == '__main__':
    folder_path = sys.argv[1]
    if os.path.basename(folder_path) in ["slam", "alignment", "alignment2", "rt"]:
        draw(os.path.basename(folder_path))
    else:
        for mode in os.listdir(folder_path):
            print mode
