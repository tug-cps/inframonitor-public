from restapi.schema.common import strict

body_schema = strict({
    'type': 'object',
    'properties': {
        'ids': {
            'type': 'array',
            'items': {'type': 'string'}
        },
        'values': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'timestamp': {'type': 'number'},
                    'values': {'type': 'array', 'items': {'type': 'number'}}
                },
            }
        },
        'created': {'type': 'number'}
    },
})
