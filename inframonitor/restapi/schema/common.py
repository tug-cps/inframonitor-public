def strict(schema: dict):
    if schema.get('type') == 'object':
        schema['additionalProperties'] = False
        schema['required'] = list(schema['properties'].keys())
    for key, value in schema.items():
        if isinstance(value, dict):
            schema[key] = strict(value)
    return schema
