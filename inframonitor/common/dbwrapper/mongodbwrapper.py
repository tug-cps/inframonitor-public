import datetime as dt

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


class MongoDBWrapper:
    def __init__(self, host, port, database, username, password, entities: str = None):
        self.__host = host
        self.__port = port
        self.__database = database
        self.__username = username
        self.__password = password
        self.__entities = entities or 'entities'
        self.client = MongoClient(self.__host, self.__port, username=self.__username, password=self.__password,
                                  authSource=self.__database, serverSelectionTimeoutMS=5000)

    @property
    def db(self) -> Database:
        return self.client[self.__database]

    @property
    def meteoblue(self) -> Collection:
        return self.db.meteoblue

    @property
    def entities(self) -> Collection:
        return self.db[self.__entities]

    def find_one(self, _filter):
        return self.entities.find_one(_filter)

    def find_simple(self, field, value) -> list:
        __filter = {field: value} if value else None
        return list(self.entities.find(__filter))

    def find(self, _filter) -> list:
        return list(self.entities.find(_filter))

    def insert(self, dictionary: dict, date_created: dt.datetime = None) -> bool:
        if date_created is None:
            date_created = dt.datetime.utcnow()
        if 'id' in dictionary:
            dictionary['_id'] = dictionary['id']
            del dictionary['id']

        assert '_id' in dictionary, 'entity must have an id'
        assert 'type' in dictionary, 'entity must have a type'

        id_split = dictionary['_id'].split(':')

        assert len(id_split) == 4, 'id must be of format urn:ngsi-ld:$TYPE:$ID'
        assert id_split[0] == 'urn', 'id must be of format urn:ngsi-ld:$TYPE:$ID'
        assert id_split[1] == 'ngsi-ld', 'id must be of format urn:ngsi-ld:$TYPE:$ID'
        assert id_split[2] == dictionary['type'], '$TYPE in urn:ngsi-ld:$TYPE:$ID must match type entry in dictionary'

        if 'dateCreated' not in dictionary:
            dictionary['dateCreated'] = {
                'type': 'DateTime',
                'value': date_created.replace(microsecond=0).isoformat()
            }

        self.entities.insert_one(dictionary)
        response = list(self.entities.find(dictionary))

        return len(response) == 1

    def update(self, _id: str, dictionary: dict, date_modified: dt.datetime = None) -> bool:
        if date_modified is None:
            date_modified = dt.datetime.utcnow()
        assert 'id' not in dictionary, 'do NOT add an id field'
        assert '_id' not in dictionary, '_id is immutable, do NOT try to update it'
        assert 'type' not in dictionary, 'type is immutable, do NOT try to update it'

        if 'dateModified' not in dictionary:
            dictionary['dateModified'] = {
                'type': 'DateTime',
                'value': date_modified.replace(microsecond=0).isoformat()
            }

        response = self.entities.update_one(
            filter={'_id': _id},
            update={
                '$set': dictionary
            }
        )
        return response.acknowledged

    def delete(self, _id: str) -> bool:
        response = self.entities.delete_one({'_id': _id})

        return response.deleted_count == 1
