import json, base64

def create_secret(name, entries):
    secret = {'metadata': { 'name': name} }
    secret['data'] = {}
    for key in entries:
        secret['data'][key] = base64.b64encode(entries[key])
    return secret

def transform(input_format):
    secret = {}
    for entry in input_format:
        secret[entry['key']] = entry['value']
    return secret
