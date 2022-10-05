from restapi.schema.common import strict

body_schema = strict({
    'type': 'object',
    'properties': {
        'dataItemValues': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'timestamp': {'type': 'number'},
                    'value': {'type': 'number'}
                },
            }
        },
        'created': {'type': 'number'}
    },
})
