import brickschema
from brickschema.namespaces import A, BRICK, UNIT
from rdflib import Literal, URIRef, BNode

from common import type_def
from common.database import get_db

if __name__ == "__main__":
    print("Convert to brick")
    mongodb_wrapper = get_db()
    entities = mongodb_wrapper.get_entities()
    haystack_buildings = []
    g = brickschema.Graph()
    for building_type in type_def.building_types:
        for building in entities.find({"type": building_type}):
            print(building)
            id = building["_id"]
            g.add((URIRef(id), A, BRICK.Building))
            if "address" in building:
                g.add((URIRef(id), BRICK.hasAddress, Literal(
                    building["address"]["value"]["streetAddress"] + ", "
                    + building["address"]["value"]["addressLocality"] + " "
                    + building["address"]["value"]["postalCode"])))

    ignored_entity_types = type_def.building_types
    unresolved_sensor_types = []
    for sensor in mongodb_wrapper.find({'type': {'$nin': ignored_entity_types}}):
        print(sensor)
        id = sensor["_id"]
        if "type" in sensor:
            if sensor["type"] == "Energy":
                g.add((URIRef(id), A, BRICK.Energy_Usage_Sensor))
                g.add((URIRef(id), BRICK.hasUnit, UNIT["KiloW-HR"]))
            elif sensor["type"] == "Water":
                g.add((URIRef(id), A, BRICK.Water_Flow_Sensor))
            elif sensor["type"] == "Humidity":
                g.add((URIRef(id), A, BRICK.Humidity_Sensor))
            elif sensor["type"] == "HumidityRelative":
                g.add((URIRef(id), A, BRICK.Relative_Humidity_Sensor))
            elif sensor["type"] == "Temperature":
                g.add((URIRef(id), A, BRICK.Temperature_Sensor))
                g.add((URIRef(id), BRICK.hasUnit, UNIT.DEG_C))
            elif sensor["type"] == "Contact":
                g.add((URIRef(id), A, BRICK.Contact_Sensor))
            elif sensor["type"] == "Enthalpy":
                g.add((URIRef(id), A, BRICK.Enthalpy_Sensor))
            elif sensor["type"] == "Power":
                g.add((URIRef(id), A, BRICK.Power_Sensor))
            elif sensor["type"] == "BatteryVoltage":
                g.add((URIRef(id), A, BRICK.Power_Sensor))
            elif sensor["type"] == "CO2":
                g.add((URIRef(id), A, BRICK.CO2_Sensor))
            elif sensor["type"] == "UnknownSensor":
                g.add((URIRef(id), A, BRICK.Battery_Voltage_Sensor))

            else:
                g.add((URIRef(id), A, BRICK.Sensor))
                unresolved_sensor_types.append(sensor["type"])
        else:
            g.add((URIRef(id), A, BRICK.Sensor))
        if "refBuilding" in sensor:
            if sensor["refBuilding"]["object"] != "":
                g.add((URIRef(id), BRICK.hasLocation, URIRef(sensor["refBuilding"]["object"])))
                if sensor["refBuilding"]["object"] == "urn:ngsi-ld:Building:Inffeldgasse16":
                    g.add((URIRef(id), BRICK.isPointOf, URIRef(sensor["refBuilding"]["object"])))
        if "name" in sensor:
            timeseries = BNode()
            g.add((timeseries, BRICK.hasTimeseriesId, Literal(sensor["name"])))
            g.add((timeseries, BRICK.storedAt, URIRef("urn:influxdb")))
            g.add((URIRef(id), BRICK.timeseries, timeseries))
    g.add((URIRef("urn:influxdb"), A, BRICK.Database))  # TODO maybe shoudln't be urn

    # TODO add unit
    # TODO check the standards for addresses

    g.expand(profile="shacl")  # infers Brick classes from Brick tags
    g.serialize("inffeldgasse.ttl", format="ttl")
    check = brickschema.Graph()
    check.load_file(("inffeldgasse.ttl"))
    valid, _, _ = check.validate()
    print(f"Graph is valid? {valid}")
    unresolved_sensor_types = set(unresolved_sensor_types)
    print("Unresolved sensor types are:")
    for type in unresolved_sensor_types:
        print(type)
