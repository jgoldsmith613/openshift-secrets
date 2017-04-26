import unittest, createSecret, base64, json

class CreateSecretsJSONTestCases(unittest.TestCase):
    def testShouldMakeSecretWithSingleKey(self):
        secretDict = {'key1':'value1'}
        name = 'somename'
        jsonSecret = createSecret.create_secret(name, secretDict)
        secret = json.loads(jsonSecret)
        assert secret['metadata']['name'] == name, 'secret name incorrect'
        assert secret['data']['key1'] == base64.b64encode('value1'), 'secret value/key not correct'

    def testShouldMakeSecretWithSingleWithMultipleValues(self):
        secretDict = {'key1':'value1', 'key2':'value2'}
        name = 'somename'
        jsonSecret = createSecret.create_secret(name, secretDict)
        secret = json.loads(jsonSecret)
        assert secret['metadata']['name'] == name, 'secret name incorrect'
        assert secret['data']['key1'] == base64.b64encode('value1'), 'secret value/key not correct'
        assert secret['data']['key2'] == base64.b64encode('value2'), 'secret value/key not correct'


        



if __name__ == "__main__":
    unittest.main()
