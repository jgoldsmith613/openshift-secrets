import requests, json, base64, urlparse, getopt, sys

def parse_opts():
	opts, args = getopt.getopt(sys.argv[1:], "i:s:P:a:v:u:p:m:", ["input-file=", "secret-name=","project-name=","application=","volume-name" ,"username=", "password=", "master-url=", "secret-content=" ])
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
                print "Project name is a required parameter, please run again with -P or --project-name"
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

def create_token():
	oauthUrl = master_url + "oauth/authorize?response_type=token&client_id=openshift-challenging-client"
	authResponse = session.get(oauthUrl, verify=False, auth=(username, password), headers={'X-CSRF-Token': 'xxx'}, allow_redirects=False)
	location = authResponse.headers['location']
	print location
	location = location[location.index('#')+1:]
	location_parsed = urlparse.parse_qs(location)
	return location_parsed['access_token'][0]


def confirm_project_exists():
	headers = { 'Authorization': 'Bearer {}'.format(token), 'Content-Type':'application/json' }
	url = master_url + "oapi/v1/projects/{}".format(project_name)
	response = session.get(url, headers=headers)
	if (response.status_code != 200):
		print "project {} does not exist in openshift.  Please use a valid project".format(project_name)
		sys.exit(1)

def confirm_new_secret_name():
	headers = { 'Authorization': 'Bearer {}'.format(token), 'Content-Type':'application/json' }
        url = master_url + "api/v1/namespaces/{}/secrets/{}".format(project_name, secret_name)
        response = session.get(url, headers=headers)
        if (response.status_code == 200):
                print "secret {} already exists in {} project, please use a unique secret name".format(secret_name, project_name)
                sys.exit(1)


def get_deploymentconfig_and_confirm_exists():
	headers = { 'Authorization': 'Bearer {}'.format(token), 'Content-Type':'application/json' }
        url = master_url + "oapi/v1/namespaces/{}/deploymentconfigs/{}".format(project_name, application_name)
        response = session.get(url, headers=headers)
	if (response.status_code != 200):
                print "deploymentconfig {} does not exists in {} project, please use a existing deploymentconfig".format(application_name, project_name)
                sys.exit(1)
	return json.loads(response.text)
	
def confirm_volume_exists():
	volumes = dc['spec']['template']['spec']['volumes']
	discovered = False
	for volume in volumes:
		if volume['name'] == volume_name:
			discovered = True
	if discovered is False:
		print "volume {} does not exist in deploymentconfig {}, please specify a known volume".format(volume_name, application_name)	
	

def make_secret():
	secret_value = choose_secret()
	payload = { 'data' : {'secret': secret_value}, 'metadata' : {'name': secret_name } }
	json_payload =  json.dumps(payload);
	url = master_url + "api/v1/namespaces/{}/secrets".format(project_name)
	headers = { 'Authorization': 'Bearer {}'.format(token), 'Content-Type':'application/json' }
	response = session.post(url, data=json_payload, headers=headers)
	if response.status_code != 201:
		print "secret failed to be created"
		sys.exit(1)

def patch_dc():
	url = master_url + "oapi/v1/namespaces/{}/deploymentconfigs/{}".format(project_name, application_name)
	patch = {'spec':{ 'template' : { 'spec': { 'volumes' : [   { 'name': volume_name, 'secret': { 'secretName': secret_name } }  ]   }   }   } }
	json_payload = json.dumps(patch)
	headers = { 'Authorization': 'Bearer {}'.format(token), 'Content-Type':'application/strategic-merge-patch+json' }
	response = session.patch(url, data=json_payload, headers=headers)
	if response.status_code != 200:
                print "deploymentconfig failed to be updated"
                sys.exit(1)	
	

input_file = None
secret_content = None
secret_name = None
project_name = None
application_name = None
volume_name = None
#Assumes you are using the CDK if you do not specify a master url, username and password
master_url = "https://10.1.2.2:8443/"
username = "admin"
password = "admin"

opts, args = parse_opts()
for opt, val in opts:
	if opt in {"-i", "--input-file"}:
		input_file = val
	if opt in {"-s", "--secret-name"}:
		secret_name = val
	if opt in {"--secret-content"}:
                secret_content = val
	if opt in {"-P", "--project-name"}:
                project_name = val
	if opt in {"-a", "--application-name"}:
                application_name = val
	if opt in {"-v", "--volume-name"}:
                volume_name = val
	if opt in {"-u", "--username"}:
                username = val
	if opt in {"-p", "--password"}:
                password = val
	if opt in {"-m", "--master-url"}:
                master_url = val
		if master_url[-1:] != "/":
			master_url = master_url + "/"


check_valid_values()

session = requests.Session()

token = create_token()

confirm_project_exists()

confirm_new_secret_name()

dc = get_deploymentconfig_and_confirm_exists()

confirm_volume_exists()

make_secret()

patch_dc()
