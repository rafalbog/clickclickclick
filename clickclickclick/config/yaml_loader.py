import os
import yaml


# Custom constructor for environment variables
def env_constructor(loader, node):
    env_var = loader.construct_scalar(node)
    return os.getenv(env_var, "")


# Register the !ENV tag in PyYAML to use the custom constructor
yaml.SafeLoader.add_constructor("!ENV", env_constructor)


# Function to load the YAML file with environment variable processing
def load_yaml(file_path, loader=yaml.SafeLoader):
    with open(file_path, "r") as file:
        return yaml.load(file, Loader=loader)
