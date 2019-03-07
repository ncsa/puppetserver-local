# Puppetserver Local Config
Local customizations for puppetserver.

## Dependencies
* Python version >= 3.6
* https://pypi.org/project/tabulate/
* https://pyyaml.org/wiki/PyYAMLDocumentation

# Installation
1. `export PUP_CUSTOM_DIR=/etc/puppetlabs/local`
1. `git clone https://github.com/ncsa/puppetserver-local.git $PUP_CUSTOM_DIR`
1. (optional) `vim $PUP_CUSTOM_DIR/config/config.ini`
1. (optional) `export PY3_PATH=</path/to/python3>`
1. `$PUP_CUSTOM_DIR/configure.sh`

# ENC
See [ENC Readme](enc/README.md)

# R10K
See [R10K Readme](r10k_postrun/README.md)
