import pymongo

if __name__ == "__main__":
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    testdb = client["testdatabase"]

    testdb.entities.drop()
    testdb.entities.insert_many([{
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
    }, {
        "_id": "urn:ngsi-ld:Energy:20_252110",
        "type": "Energy",
        "name": "20_252110",
        "description": "Trafo Allgemein",
        "reading": 1448429.824,
        "refBuilding": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:Building:Inffeldgasse25b"
        },
        "dateModified": {
            "type": "DateTime",
            "value": "2021-12-03T07:00:00"
        }
    }, {
        "_id": "urn:ngsi-ld:Energy:30_120110",
        "type": "Energy",
        "name": "30_120110",
        "reading": 11115962.88,
        "dateModified": {
            "type": "DateTime",
            "value": "2021-12-03T07:00:05"
        }
    }, {
        "_id": "urn:ngsi-ld:Energy:20_260110",
        "type": "Energy",
        "name": "20_260110",
        "reading": 4332.36,
        "dateModified": {
            "type": "DateTime",
            "value": "2021-12-03T07:00:00"
        }
    }, {
        "_id": "urn:ngsi-ld:Energy:10_160110",
        "type": "Energy",
        "name": "10_160110",
        "reading": 2126260.864,
        "dateModified": {
            "type": "DateTime",
            "value": "2021-12-03T07:00:00"
        }
    }, {
        "_id": "urn:ngsi-ld:Energy:20_255111",
        "type": "Energy",
        "name": "20_255111",
        "description": "IN25E-ST1_BS",
        "reading": 17458.33,
        "refBuilding": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:Building:Inffeldgasse25e"
        },
        "dateModified": {
            "type": "DateTime",
            "value": "2021-12-03T07:00:00"
        }
    }, {
        "_id": "urn:ngsi-ld:Energy:20_330110",
        "type": "Energy",
        "name": "20_330110",
        "description": "Trafo 1",
        "reading": 36682.008,
        "refBuilding": {
            "type": "Relationship",
            "object": "urn:ngsi-ld:Building:Inffeldgasse33"
        },
        "dateModified": {
            "type": "DateTime",
            "value": "2021-12-03T07:00:00"
        },
        "maxPrediction": 18.54423713684082,
        "minPrediction": 2.69180974025974
    }])

    testdb.entities.insert_many([
        {
            "_id": "urn:ngsi-ld:Building:Inffeldgasse33",
            "type": "Building",
            "category": {
                "type": "Property",
                "value": [
                    "office",
                    "lab"
                ]
            },
            "address": {
                "type": "Property",
                "value": {
                    "addressLocality": "Graz",
                    "postalCode": "8010",
                    "streetAddress": "Inffeldgasse 33",
                    "type": "PostalAddress"
                }
            },
            "@context": [
                "https://schema.lab.fiware.org/ld/context",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
            ]
        }, {
            "_id": "urn:ngsi-ld:Building:Inffeldgasse13",
            "type": "Building",
            "category": {
                "type": "Property",
                "value": [
                    "office",
                    "lab"
                ]
            },
            "address": {
                "type": "Property",
                "value": {
                    "addressLocality": "Graz",
                    "postalCode": "8010",
                    "streetAddress": "Inffeldgasse 13",
                    "type": "PostalAddress"
                }
            },
            "@context": [
                "https://schema.lab.fiware.org/ld/context",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
            ]
        }, {
            "_id": "urn:ngsi-ld:Building:Inffeldgasse25a",
            "type": "Building",
            "category": {
                "type": "Property",
                "value": [
                    "office",
                    "lab"
                ]
            },
            "address": {
                "type": "Property",
                "value": {
                    "addressLocality": "Graz",
                    "postalCode": "8010",
                    "streetAddress": "Inffeldgasse 25a",
                    "type": "PostalAddress"
                }
            },
            "@context": [
                "https://schema.lab.fiware.org/ld/context",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
            ]
        }, {
            "_id": "urn:ngsi-ld:Building:Inffeldgasse25b",
            "type": "Building",
            "category": {
                "type": "Property",
                "value": [
                    "office",
                    "lab"
                ]
            },
            "address": {
                "type": "Property",
                "value": {
                    "addressLocality": "Graz",
                    "postalCode": "8010",
                    "streetAddress": "Inffeldgasse 25b",
                    "type": "PostalAddress"
                }
            },
            "@context": [
                "https://schema.lab.fiware.org/ld/context",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
            ]
        }, {
            "_id": "urn:ngsi-ld:Building:Inffeldgasse25c",
            "type": "Building",
            "category": {
                "type": "Property",
                "value": [
                    "office",
                    "lab"
                ]
            },
            "address": {
                "type": "Property",
                "value": {
                    "addressLocality": "Graz",
                    "postalCode": "8010",
                    "streetAddress": "Inffeldgasse 25c",
                    "type": "PostalAddress"
                }
            },
            "@context": [
                "https://schema.lab.fiware.org/ld/context",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
            ]
        }, {
            "_id": "urn:ngsi-ld:Building:Inffeldgasse25d",
            "type": "Building",
            "category": {
                "type": "Property",
                "value": [
                    "office",
                    "lab"
                ]
            },
            "address": {
                "type": "Property",
                "value": {
                    "addressLocality": "Graz",
                    "postalCode": "8010",
                    "streetAddress": "Inffeldgasse 25d",
                    "type": "PostalAddress"
                }
            },
            "@context": [
                "https://schema.lab.fiware.org/ld/context",
                "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
            ]
        }
    ])
