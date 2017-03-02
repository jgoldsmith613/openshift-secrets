import requests, json, base64, urlparse, getopt, sys, os


def create_token():
	oauthUrl = master_url + "oauth/authorize?response_type=token&client_id=openshift-challenging-client"
        with open(login_creds, 'r') as f:
            first_line = f.readline()
        creds = first_line.strip().split('=')
        authResponse = session.get(oauthUrl, verify=False, auth=(creds[0], creds[1]), headers={'X-CSRF-Token': 'xxx'}, allow_redirects=False)
	location = authResponse.headers['location']
	location = location[location.index('#')+1:]
	location_parsed = urlparse.parse_qs(location)
	return location_parsed['access_token'][0]


def get_projects():
	headers = { 'Authorization': 'Bearer {}'.format(token), 'Content-Type':'application/json' }
	url = master_url + "oapi/v1/projects"
	response = session.get(url, headers=headers)
        projects = json.loads(response.text)
	if (response.status_code != 200):
		print "error in get_projects"
                print response.status_code
                print response.text
		sys.exit(1)
        return projects["items"]

def filter_projects():
        filtered_projects = []
        for project in projects:
            name = project["metadata"]["name"]
            if name.startswith(project_prefix):
                filtered_projects.append(name)
        return filtered_projects


def parse_file():
        split = os.path.basename(file_path).split("_")
        return (split[0], split[1])

def get_deploymentconfigs(project):
        headers = { 'Authorization': 'Bearer {}'.format(token), 'Content-Type':'application/json' }
        url = master_url + "oapi/v1/namespaces/{}/deploymentconfigs".format(project)
        response = session.get(url, headers=headers)
        if (response.status_code != 200):
                print "project does not exist: {}".format( project)
                sys.exit(1)
        return json.loads(response.text)

def search_deployment_configs(project):
        dcs = get_deploymentconfigs(project)
        selected_dcs = []
        for dc in dcs["items"]:
            for volume in dc["spec"]["template"]["spec"]["volumes"]:
                if volume["secret"] != None:
                    if volume["secret"]["secretName"] == secret_name:
                        selected_dcs.append(dc["metadata"]["name"])
        return selected_dcs
        


def apply_secret(project):
	secret_value = base64.b64encode(file(file_path).read())
	payload = { 'data' : {'secret': secret_value}, 'metadata' : {'name': secret_name } }
	json_payload =  json.dumps(payload);
	url = master_url + "api/v1/namespaces/{}/secrets/{}".format(project, secret_name)
	headers = { 'Authorization': 'Bearer {}'.format(token), 'Content-Type':'application/json' }
	response = session.put(url, data=json_payload, headers=headers)
	if response.status_code != 200:
		print "secret failed to be updated"
                print response.status_code
                print response.text
		sys.exit(1)

def deploy_dc(project, dc):
        payload = { 'name' : dc, 'latest' : True, 'force': True }
        json_payload =  json.dumps(payload);
        url = master_url + "oapi/v1/namespaces/{}/deploymentconfigs/{}/instantiate".format(project, dc)
        headers = { 'Authorization': 'Bearer {}'.format(token), 'Content-Type':'application/json' }
        response = session.post(url, data=json_payload, headers=headers)
        print response.status_code
        if response.status_code != 201:
                print "deployment request failed to be created"
                print response.status_code
                print response.text
                sys.exit(1)

    

#Assumes you are using the CDK if you do not specify a master url, username and password
master_url = "https://192.168.122.237:8443/"
login_creds = "test/creds"
file_path = "test/test_test-secret"
project_prefix = None
secret_name = None


project_prefix, secret_name = parse_file()

session = requests.Session()

token = create_token()

projects = get_projects()

filtered_projects = filter_projects()

for project in filtered_projects:
        selected_dcs = search_deployment_configs(project)
        apply_secret(project)
        for dc in selected_dcs:
            deploy_dc(project, dc)


