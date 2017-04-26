import urlparse, argparse, createSecret, ocpRequests


def parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('-m', '--master-url', dest='master_url', required=True)
        parser.add_argument('-l', '--login-creds', dest='login_creds', required=True)
        parser.add_argument('-p', '--project', dest='project', required=True)        
        args = parser.parse_args()
        return args.master_url, args.login_creds, args.project

def parse_login_file():
    with open(login_creds, 'r') as f:
            first_line = f.readline()
    creds = first_line.strip().split('=')
    return creds[0], creds[1]

master_url, login_creds, project = parse_args()
username, password = parse_login_file()
secret_entries = {'key7': 'value4', 'key2': 'value3'}
secret_name = 'test'

secret = createSecret.create_secret(secret_name, secret_entries)
token = ocpRequests.create_token(master_url, username, password)
ocpRequests.apply_secret(master_url, token, project, secret, secret_name)





