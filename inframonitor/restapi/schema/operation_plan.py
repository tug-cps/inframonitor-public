from restapi.schema.common import strict

body_schema = strict({
    'type': 'object',
    'properties': {
        'info': {
            'type': 'object',
            'properties': {
                'status': {'type': 'string'},
                'timestamp': {'type': 'string'},

            },
        },
        'schedules': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string'},
                    'description': {'type': 'string'},
                    'unit': {'type': 'string'},
                    'values': {'type': 'array', 'items': {'type': 'number'}},
                    'timestamps': {'type': 'array', 'items': {'type': 'string'}}
                },
            },
        },
    },
})
