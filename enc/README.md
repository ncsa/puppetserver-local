# Puppet External Node Classifier (ENC)
Setup and manage a database to use for puppet ENC

# Quickstart
### Create DB
1. `vim tables.yaml`
1. `admin.py --init`

### Initialize DB contents
##### Using a CSV file
1. `admin.py --mkcsv > source.csv`
1. `vim source.csv`
1. `admin.py --add --csv source.csv`
##### Using a Yaml file
1. `admin.py --mkyaml > source.yaml`
1. `vim source.yaml`
1. `admin.py --add --yaml source.yaml`

### Test puppet lookup of FQDN
1. `admin.py <FQDN_of_puppet_client_node>`

# Administration of the ENC database
### Add nodes from Yaml file
1. `admin.py --add --yaml source.yaml`
### Add nodes from CSV file
1. `admin.py --add --csv source.csv`
### Add nodes from cmdline
1. `admin.py --add --site <SITENAME> --datacenter <DATACENTERNAME> --cluster <CLUSTERNAME> --role <ROLENAME> --environment <ENVIRONMENTNAME> <FQDN_of_puppet_client_node>`

### Change nodes
