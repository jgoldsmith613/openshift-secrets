import requests, urlparse

def create_token(master_url, username, password):
        session = requests.Session()
        oauthUrl = master_url + "oauth/authorize?response_type=token&client_id=openshift-challenging-client"
        authResponse = session.get(oauthUrl, verify=False, auth=(username, password), headers={'X-CSRF-Token': 'xxx'}, allow_redirects=False)
        location = authResponse.headers['location']
        location = location[location.index('#')+1:]
        location_parsed = urlparse.parse_qs(location)
        return location_parsed['access_token'][0]

def check_secret(master_url, token, project, secret_name):
        session = requests.Session()
        url = master_url + "api/v1/namespaces/{}/secrets/{}".format(project, secret_name)
        headers = { 'Authorization': 'Bearer {}'.format(token), 'Content-Type':'application/json' }
        response = session.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return True
        if response.status_code == 404:
            return False
        else:
            print "failed to check if secret exists"
            sys.exit(1)


def apply_secret(master_url, token, project, secret, secret_name):
        session = requests.Session()
	headers = { 'Authorization': 'Bearer {}'.format(token), 'Content-Type':'application/json' }
        if check_secret(master_url, token, project, secret_name):
            url = master_url + "api/v1/namespaces/{}/secrets/{}".format(project, secret_name)
	    response = session.put(url, data=secret, headers=headers, verify=False)
        else:
            url = master_url + "api/v1/namespaces/{}/secrets".format(project)
            response = session.post(url, data=secret, headers=headers, verify=False)
        if not (response.status_code == 200 or response.status_code == 201):
		print "secret failed to be created/updated"
                print response.status_code
                print response.text
		sys.exit(1)

