from unittest.mock import Mock

from admin.update_influxdb import update_from_mongodb

influxdb_wrapper = Mock()
influxdb_wrapper.add_tags = Mock(return_value=None)

mongodb_wrapper = Mock()
mongodb_wrapper.find = Mock(return_value=[{
    "_id": "urn:ngsi-ld:Water:In1In11K1_S001_S94_P01_Vol",
    "type": "Water",
    "name": "In1In11K1_S001_S94_P01_Vol",
    "reading": 3948.85205,
    "dateModified": {
        "type": "DateTime",
        "value": "2021-12-03T07:07:08"
    }
}, {
    "_id": "urn:ngsi-ld:Water:In1L33AK1_S0102_P101_Vol",
    "type": "Water",
    "name": "In1L33AK1_S0102_P101_Vol",
    "description": "Nutzwasserzaehler IN33-WNUTZ",
    "reading": 740.08002,
    "refBuilding": {
        "type": "Relationship",
        "object": "urn:ngsi-ld:Building:Inffeldgasse33"
    },
    "dateModified": {
        "type": "DateTime",
        "value": "2021-12-03T07:05:00"
    }
}, {
    "_id": "urn:ngsi-ld:Water:In1L33AK1_S0102_P201_Vol",
    "type": "Water",
    "name": "In1L33AK1_S0102_P201_Vol",
    "description": "Wasserzaehler IN33-WSTADT",
    "reading": 257.03699,
    "refBuilding": {
        "type": "Relationship",
        "object": "urn:ngsi-ld:Building:Inffeldgasse33"
    },
    "dateModified": {
        "type": "DateTime",
        "value": "2021-12-03T07:13:01"
    },
    "maxPrediction": 0.304179847240448,
    "minPrediction": 0.0002011433243751526
}]
)


def test_update_influxdb():
    updates = update_from_mongodb(influxdb_wrapper, mongodb_wrapper)
    assert updates == 3
    influxdb_wrapper.add_tags.assert_called_with("In1L33AK1_S0102_P201_Vol",
                                                 {"type": "Water", "id": "urn:ngsi-ld:Water:In1L33AK1_S0102_P201_Vol"})
