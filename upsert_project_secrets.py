import urlparse, argparse, createSecret, ocpRequests, yaml, sys, os, shutil


def parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('-m', '--master-url', dest='master_url', required=True)
        parser.add_argument('-l', '--login-creds', dest='login_creds', required=True)
        parser.add_argument('-f', '--file', dest='file', required=True)        
        args = parser.parse_args()
        return args.master_url, args.login_creds, args.file

def parse_login_file():
    with open(login_creds, 'r') as f:
            first_line = f.readline()
    creds = first_line.strip().split('=')
    return creds[0], creds[1]

def load_yaml_file(input_file):
    with open(input_file, 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit(1)

def get_alias_from_cyberark(alias):
    #This still needs to be done
    return alias

def make_secret(secret):
    for entry in secret['data']:
        entry['value'] = get_alias_from_cyberark(entry['alias'])
    transformed = createSecret.transform(secret['data'])
    ocp_secret = createSecret.create_secret(secret['name'], transformed)
    ocpRequestor.apply_secret(ocp_secret)

def load_props(path):
    props = {}
    with open(path) as f:
        for line in f:
            key, value = line.strip().split('=')
            props[key] = value
    return props

def archive_file(secret_file):
    shutil.move(secret_file, os.path.join(archive_dir, os.path.basename(secret_file) ))





props = load_props('cfg/secrets.cfg')
master_url = props['OCP_MASTER_URL']
login_creds = props['PATH_OF_CREDS_FILE']
trigger_path = props['PATH_OF_TRG_YAML_FILES']
archive_dir = props['YAML_ARCHIVE_DIR']

username, password = parse_login_file()

for trigger_file in os.listdir(trigger_path):
    if trigger_file.endswith(".yaml"):
        secret_file = os.path.join(trigger_path, trigger_file)
        parsed_file = load_yaml_file(secret_file)
        archive_file(secret_file)
        project = parsed_file['project']
        ocpRequestor = ocpRequests.OCPRequests(master_url, username, password, project)
        
        for secret in parsed_file['secrets']:
            make_secret(secret)



