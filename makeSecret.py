import requests, json, base64, urlparse, getopt, sys


def parse_opts():
	opts, args = getopt.getopt(sys.argv[1:], "i:s:p:a:v:", ["input-file=", "secret-name=","project-name=","application=","volume-name" , "secret-content=" ])
	return opts, args	

def check_valid_values():
	if input_file is None and secret_content is None:
        	print "Either input file or secret content must be specified, please run again with -i, --input-file or --secret-content"
        	sys.exit(1)
	if input_file is not None and secret_content is not None:
                print "Only one of input file or secret content must be specified, please run again with -i, --input-file or --secret-content, but not more than one"
                sys.exit(1)
	if secret_name is None:
        	print "Secret name is a required parameter, please run again with -s or --secret-name"
        	sys.exit(1)
	if project_name is None:
                print "Project name is a required parameter, please run again with -p or --project-name"
                sys.exit(1)
	if application_name is None:
                print "Application name is a required parameter, please run again with -a or --application-name"
                sys.exit(1)
	if volume_name is None:
                print "volume name is a required parameter, please run again with -v or --volume-name"
                sys.exit(1)


def choose_secret():
	if input_file is not None:
		return base64.b64encode(file(input_file).read())
	else:
		return base64.b64encode(secret_content)

input_file = None
secret_content = None
secret_name = None
project_name = None
application_name = None
volume_name = None

opts, args = parse_opts()
for opt, val in opts:
	if opt in {"-i", "--input-file"}:
		input_file = val
	if opt in {"-s", "--secret-name"}:
		secret_name = val
	if opt in {"--secret-content"}:
                secret_content = val
	if opt in {"-p", "--project-name"}:
                project_name = val
	if opt in {"-a", "--application-name"}:
                application_name = val
	if opt in {"-v", "--volume-name"}:
                volume_name = val


check_valid_values()

session = requests.Session()

oauthUrl = "https://10.1.2.2:8443/oauth/authorize?response_type=token&client_id=openshift-challenging-client"

authResponse = session.get(oauthUrl, verify=False, auth=('admin', 'admin'), headers={'X-CSRF-Token': 'xxx'}, allow_redirects=False)

location = authResponse.headers['location']

location = location[location.index('#')+1:]

location_parsed = urlparse.parse_qs(location)

token = location_parsed['access_token'][0]


secret_value = choose_secret()

payload = { 'data' : {'secret': secret_value}, 'metadata' : {'name': secret_name } } 
json_payload =  json.dumps(payload);
print json_payload
secret_url = "https://10.1.2.2:8443/api/v1/namespaces/{}/secrets".format(project_name)

secret_headers = { 'Authorization': 'Bearer {}'.format(token), 'Content-Type':'application/json' }

secret_response = session.post(secret_url, data=json_payload, headers=secret_headers)

print secret_response.text

dc_url = "https://10.1.2.2:8443/oapi/v1/namespaces/{}/deploymentconfigs/{}".format(project_name, application_name)

patch = {'spec':{ 'template' : { 'spec': { 'volumes' : [   { 'name': volume_name, 'secret': { 'secretName': secret_name } }  ]   }   }   } }

patch_payload = json.dumps(patch)

patch_headers = { 'Authorization': 'Bearer {}'.format(token), 'Content-Type':'application/strategic-merge-patch+json' }

patch_response = session.patch(dc_url, data=patch_payload, headers=patch_headers)

print patch_response.text





