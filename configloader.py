import argparse
import yaml
import os

DEFAULT_ENV = "dev"
SECRETS_LOCATION = "config/secrets.yaml"

parser = argparse.ArgumentParser()
parser.add_argument("--env", help="set the runtime environment")
parser.set_defaults(env=DEFAULT_ENV)

args = parser.parse_args()

env = args.env


def load_env(relative_file_path):
    try:
        with open(relative_file_path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            for key in data.keys():
                os.environ[key] = data[key]
            print(f"Config loaded from {f.name}")
    except Exception as error:
        print("Error reading file: ", error)
        raise error


load_env(f'config/{env}.yaml')
load_env(SECRETS_LOCATION)
