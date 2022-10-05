from flask import abort
from flask.views import MethodView

from restapi.db import database


class BricksensorView(MethodView):

    def __init__(self):
        super().__init__()
        self.graph = database.get_ontology()

    def search(self):  # TODO Add site
        try:
            names = self.graph.query("""SELECT ?name {\
                ?timeseries brick:hasTimeseriesId ?name .\
                }""")

            sensors_metadata = []

            for nameinfo in names:
                name = str(nameinfo.name)
                assert type(name) is str

                # TODO Portable for all nested relations
                timeseries_info = self.graph.query("""SELECT ?tspred ?tsobj {
                                ?id brick:timeseries ?timeseries .\
                                ?timeseries ?tspred ?tsobj .\
                                ?timeseries brick:hasTimeseriesId""" + ' \"' + name + '\"' + """.\
                            }""")

                timeseries_metadata = {}

                for tsrelation in timeseries_info:
                    timeseries_metadata[tsrelation.tspred] = tsrelation.tsobj

                sensor_info = self.graph.query("""SELECT ?id ?p ?o ?timeseries {
                                ?id brick:timeseries ?timeseries.\
                                ?timeseries brick:hasTimeseriesId""" + ' \"' + name + '\"' + """.\
                                ?id ?p ?o.\
                            }""")

                sensor_id = 0
                for sensor in sensor_info:
                    sensor_id = sensor.id

                metadata = {}

                for sensor in sensor_info:
                    if sensor.o == sensor.timeseries:
                        metadata[sensor.p] = timeseries_metadata
                    else:
                        metadata[sensor.p] = sensor.o
                sensors_metadata.append({sensor_id: metadata})

            if len(sensors_metadata) == 0:
                abort(404)

            return sensors_metadata
        except StopIteration:
            abort(404)

    def get(self, name):
        try:
            assert type(name) is str

            # TODO Portable for all nested relations
            timeseries_info = self.graph.query("""SELECT ?tspred ?tsobj {
                            ?id brick:timeseries ?timeseries .\
                            ?timeseries ?tspred ?tsobj .\
                            ?timeseries brick:hasTimeseriesId""" + ' \"' + name + '\"' + """.\
                        }""")

            timeseries_metadata = {}

            for tsrelation in timeseries_info:
                timeseries_metadata[tsrelation.tspred] = tsrelation.tsobj

            sensor_info = self.graph.query("""SELECT ?id ?p ?o ?timeseries {
                            ?id brick:timeseries ?timeseries.\
                            ?timeseries brick:hasTimeseriesId""" + ' \"' + name + '\"' + """.\
                            ?id ?p ?o.\
                        }""")

            sensor_id = 0
            for sensor in sensor_info:
                sensor_id = sensor.id

            if sensor_id == 0:
                abort(404)

            metadata = {}

            for sensor in sensor_info:
                if sensor.o == sensor.timeseries:
                    metadata[sensor.p] = timeseries_metadata
                else:
                    metadata[sensor.p] = sensor.o

            return {sensor_id: metadata}

        except StopIteration:
            abort(404)
