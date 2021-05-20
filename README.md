# brazfoot_cli

## _Brazillian Football Web Scrapper CLI_ :brazil: :soccer:

### Description

**brazfoot_cli** is a CLI application written in Python that extracts information about brazillian football competitions and save them as structured file format (`json`, `xml` and `csv`) into the [export](export/) folder.

### Local setup

**brazfoot_cli** requires [Python 3.9+](https://www.python.org/downloads/).

```sh
# Clone this repository:
$ git clone https://github.com/krauss/brazfoot_cli.git
```
```sh
# Change directory
$ cd brazfoot_cli
```
```sh
# Create a virtual environment
$ python -m venv ./venv
```
```sh
# Activate the virtual environment
$ ./venv/bin/activate
```
```sh
# Install brazfoot_cli dependencies
$ pip install -r requirements.txt
```
```sh
# Run brazfoot_cli application
$ python src/main.py
$ python src/main.py --help  # to check the available command options 
```
```sh
# To exit the virtual environment
$ deactivate
```

### [Docker](https://hub.docker.com/r/jrkrauss/brazfoot_cli) setup :whale:

To quickly try this out, download our image and run it following the steps below:

```sh
# Download the image from Docker Hub
$ docker pull jrkrauss/brazfoot_cli:latest
```
```sh
# [LINUX] Run the container specifying a volume for the resulting json file 
$ docker run -it -v $PWD/export:/usr/src/app/export  jrkrauss/brazfoot_cli:latest
```
```sh
# [WINDOWS] Run the container specifying a volume for the resulting json file
$ docker run -it -v %USERPROFILE%\export:/usr/src/app/export  jrkrauss/brazfoot_cli:latest 

```