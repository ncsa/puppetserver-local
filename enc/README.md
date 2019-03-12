# Puppet External Node Classifier (ENC)
Setup and manage a database to use for puppet ENC

# Quickstart
1. `admin.py --help`

### Create DB
1. `vim tables.yaml`
1. `admin.py --init`

### Add self to DB
1. `admin.py --add --fqdn $(hostname -f) $(hostname -f)`

### Add multiple nodes to DB
##### Using a CSV file
1. `admin.py --mkcsv > source.csv`
1. `vim source.csv`
1. `admin.py --add --csv source.csv`
##### Using a Yaml file
1. `admin.py --mkyaml > source.yaml`
1. `vim source.yaml`
1. `admin.py --add --yaml source.yaml`

### Test puppet lookup of FQDN
* `admin.py <FQDN_of_puppet_client_node>`

### List all nodes in DB
* `admin.py -l`

### Working with multiple nodes
All commands `--add`, `--change`, `--del` support input from a yaml or a csv file. This is the best way to specify multiple nodes.
* `admin.py --ch --yaml filename.yaml`
* `admin.py --del --csv filename.csv`
