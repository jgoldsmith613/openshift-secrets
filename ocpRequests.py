import requests, urlparse, json, sys

class OCPRequests:


    def __init__(self, master_url, username, password, project):
            self.master_url = master_url
            self.token = self.create_token( username, password)
            self.project = project
        
    def create_token(self, username, password):
            session = requests.Session()
            oauthUrl = self.master_url + "oauth/authorize?response_type=token&client_id=openshift-challenging-client"
            authResponse = session.get(oauthUrl, verify=False, auth=(username, password), headers={'X-CSRF-Token': 'xxx'}, allow_redirects=False)
            location = authResponse.headers['location']
            location = location[location.index('#')+1:]
            location_parsed = urlparse.parse_qs(location)
            return location_parsed['access_token'][0]
    
    def check_secret(self, secret_name):
            session = requests.Session()
            url = self.master_url + "api/v1/namespaces/{}/secrets/{}".format(self.project, secret_name)
            headers = { 'Authorization': 'Bearer {}'.format(self.token), 'Content-Type':'application/json' }
            response = session.get(url, headers=headers, verify=False)
            if response.status_code == 200:
                return True
            if response.status_code == 404:
                return False
            else:
                print "failed to check if secret exists"
                sys.exit(1)
    
    
    def apply_secret(self, secret):
            session = requests.Session()
    	    headers = { 'Authorization': 'Bearer {}'.format(self.token), 'Content-Type':'application/json' }
            secret_name = secret['metadata']['name']
            if self.check_secret(secret_name):
                url = self.master_url + "api/v1/namespaces/{}/secrets/{}".format(self.project, secret_name)
    	        response = session.put(url, data=json.dumps(secret), headers=headers, verify=False)
            else:
                url = self.master_url + "api/v1/namespaces/{}/secrets".format(self.project)
                response = session.post(url, data=json.dumps(secret), headers=headers, verify=False)
            if not (response.status_code == 200 or response.status_code == 201):
    		print "secret failed to be created/updated"
                print response.status_code
                print response.text
    		sys.exit(1)

    def get_deploymentconfigs(self):
        session = requests.Session()
        headers = { 'Authorization': 'Bearer {}'.format(self.token), 'Content-Type':'application/json' }
        url = self.master_url + "oapi/v1/namespaces/{}/deploymentconfigs".format(self.project)
        response = session.get(url, headers=headers, verify=False)
        if (response.status_code != 200):
                print "project does not exist: {}".format( project)
                sys.exit(1)
        return json.loads(response.text)

    def deploy_dc(self, dc):
        session = requests.Session()
        payload = { 'name' : dc, 'latest' : True, 'force': True }
        json_payload =  json.dumps(payload);
        url = self.master_url + "oapi/v1/namespaces/{}/deploymentconfigs/{}/instantiate".format(self.project, dc)
        headers = { 'Authorization': 'Bearer {}'.format(self.token), 'Content-Type':'application/json'}
        response = session.post(url, data=json_payload, headers=headers, verify=False)
        if response.status_code != 201:
                print "deployment request failed to be created"
                print response.status_code
                print response.text
                sys.exit(1)


