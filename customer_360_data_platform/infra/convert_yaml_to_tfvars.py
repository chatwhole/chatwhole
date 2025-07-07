import yaml

def convert_yaml_to_tfvars(yaml_file, tfvars_file):
    with open(yaml_file, 'r') as yf:
        data = yaml.safe_load(yf)

    with open(tfvars_file, 'w') as tf:
        for key, value in data.items():
            if isinstance(value, str):
                tf.write(f'{key} = "{value}"\n')
            elif isinstance(value, bool):
                tf.write(f'{key} = {str(value).lower()}\n')
            else:
                tf.write(f'{key} = {value}\n')

if __name__ == "__main__":
    convert_yaml_to_tfvars('variables.yaml', 'terraform.tfvars')
    print("Converted variables.yaml to terraform.tfvars")
