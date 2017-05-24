import unittest, secretUtils, base64, json

class SecretUtilsJSONTestCases(unittest.TestCase):
    def testShouldMakeSecretWithSingleKey(self):
        secretDict = {'key1':'value1'}
        name = 'somename'
        secret = secretUtils.create_secret(name, secretDict)
        assert secret['metadata']['name'] == name, 'secret name incorrect'
        assert secret['data']['key1'] == base64.b64encode('value1'), 'secret value/key not correct'

    def testShouldMakeSecretWithSingleWithMultipleValues(self):
        secretDict = {'key1':'value1', 'key2':'value2'}
        name = 'somename'
        secret = secretUtils.create_secret(name, secretDict)
        assert secret['metadata']['name'] == name, 'secret name incorrect'
        assert secret['data']['key1'] == base64.b64encode('value1'), 'secret value/key not correct'
        assert secret['data']['key2'] == base64.b64encode('value2'), 'secret value/key not correct'

    def testShouldMakeSecretDict(self):
        secretFileFormat=[{'key': 'key1', 'value':'value1'}, {'key': 'key2', 'value':'value2'}]
        actual = secretUtils.transform(secretFileFormat)
        expected = {'key1':'value1', 'key2':'value2'}
        assert actual == expected, 'secret transformation not correct'

        



if __name__ == "__main__":
    unittest.main()
