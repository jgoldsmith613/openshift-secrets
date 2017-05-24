import urlparse, argparse, secretUtils, ocpRequests, yaml, sys, os, shutil

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
    transformed = secretUtils.transform(secret['data'])
    ocp_secret = secretUtils.create_secret(secret['name'], transformed)
    ocpRequestor.apply_secret(ocp_secret)

def load_props(path):
    props = {}
    with open(path) as f:
        for line in f:
            key, value = line.strip().split('=')
            props[key] = value
    return props

def load_archive(secret_file):
    archive_path = os.path.join(archive_dir, os.path.basename(secret_file))
    if os.path.isfile(archive_path):
        return load_yaml_file(archive_path)
    return {}

def archive_file(secret_file):
    archive_path = os.path.join(archive_dir, os.path.basename(secret_file))
    exists = os.path.isfile(archive_path)
    shutil.move(secret_file, archive_path )

def get_archive_secret(secret, archive):
    name = secret['name']
    if archive != {}:
        for archive_secret in archive['secrets']:
            if archive_secret['name'] == name:
                return archive_secret
    return {}



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
        archived_file = load_archive(secret_file)
        project = parsed_file['project']
        ocpRequestor = ocpRequests.OCPRequests(master_url, username, password, project)
        
        for secret in parsed_file['secrets']:
            if get_archive_secret(secret, archived_file) != secret:
                print secret
                make_secret(secret)
        
        archive_file(secret_file)


