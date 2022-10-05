import json

import click

from common.dbwrapper import MongoDBWrapper

db_wrapper = MongoDBWrapper('localhost', 27017, 'ontology')


@click.group()
def cli():
    """
    Command line tool for ontology database\n
    can be used to CRUD buildings and sensors
    """
    pass


@cli.command('list')
@click.option('-t', '--type')
def list(type):
    """
    list all entities, -t or --type to filter for type
    """
    response = db_wrapper.find_simple('type', type)
    print(response)


@cli.command('find')
@click.argument('field')
@click.argument('value')
def find(field, value):
    """
    find entity by a field / value combination
    """
    response = db_wrapper.find_simple(field, value)
    print(response)


@cli.command('insert')
@click.argument('dictionary')
def insert(dictionary):
    """
    insert new entity, data as dictionary
    """
    dictionary = json.loads(dictionary)
    response = db_wrapper.insert(dictionary)
    print('entity was {}.'.format('inserted' if response else 'NOT inserted'))


@cli.command('update')
@click.argument('id')
@click.argument('dictionary')
def update(_id, dictionary):
    """
    update existing entity, id and dictionary with fields to update
    """
    dictionary = json.loads(dictionary)
    response = db_wrapper.update(_id, dictionary)
    print('entity was {}.'.format('updated' if response else 'NOT updated'))


@cli.command('delete')
@click.argument('id')
def delete(_id):
    """
    delete entity by id
    """
    response = db_wrapper.find_simple('_id', _id)
    assert len(response) == 1, 'no entity found for id [{}]'.format(_id)

    print('deleting entity: {}'.format(response[0]))
    if click.confirm('are you sure you want to delete?'):
        response = db_wrapper.delete(_id)
        print('entity was {}.'.format('deleted' if response else 'NOT deleted'))


if __name__ == '__main__':
    cli()
