# brazfoot_cli

## _Brazillian Football Web Scrapper CLI_ :brazil: :soccer:

### Description

**brazfoot_cli** is a CLI application written in Python that extracts information about brazillian football competitions and save them as structured file format (`json`, `xml` and `csv`) into the [export](export/) folder.

### Local setup

**brazfoot_cli** requires [Python 3.9+](https://www.python.org/downloads/).

```sh
# Clone this repository:
$ git clone https://github.com/krauss/brazfoot_cli.git

# Change directory
$ cd brazfoot_cli

# Create a virtual environment
$> python -m venv ./venv

# Activate the virtual environment
$> ./venv/bin/activate

# Install brazfoot_cli dependencies
$> pip install -r requirements.txt

# Run brazfoot_cli application
$ python src/main.py
$ python src/main.py --help  # to check the available command options 

# To exit the virtual environment
$ deactivate
```

### Docker setup :whale:

```sh
# Clone this repository:
$ git clone https://github.com/krauss/brazfoot_cli.git

# Change directory
$ cd brazfoot_cli

# Build the Docker container
$ docker build -t brazfoot_cli .

# Run the container specifying a volume for the json file 
$ docker run -it -v $PWD/export:/usr/src/app/export  brazfoot_cli  # Linux

$ docker run -it -v %USERPROFILE%\export:/usr/src/app/export  brazfoot_cli  # Windows

```