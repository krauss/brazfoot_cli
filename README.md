# brazfoot_cli

## _Brazillian Football Web Scrapper CLI_ :brazil: :soccer:

### Description

**brazfoot_cli** is a CLI application written in Python that extracts information about brazillian football competitions and save them as structured file format (`json`, `xml` and `csv`) into the [export](export/) folder.

### Local setup

**brazfoot_cli** requires [Python 3.9+](https://www.python.org/downloads/).
Execute the commands below to setup the application according to your platform; Linux or Windows only.

#### Linux  :penguin:

* Clone this repository:
```sh
git clone https://github.com/krauss/brazfoot_cli.git
```
* Change directory:
```sh
cd brazfoot_cli
```
* Create a virtual environment:
```sh
python -m venv venv
```
* Activate the virtual environment:
```sh
source venv/bin/activate
```
* Install brazfoot_cli dependencies:
```sh
pip install -r requirements.txt
```
* Run brazfoot_cli application:
```sh
python src/main.py
```
* to check the available command options:
```sh
python src/main.py --help
```
* To exit the virtual environment:
```sh
deactivate
```

#### Windows  :tv:

* Clone this repository:
```sh
git clone https://github.com/krauss/brazfoot_cli.git
```
* Change directory:
```sh
cd brazfoot_cli
```
* Create a virtual environment:
```sh
python -m venv venv
```
* Activate the virtual environment:
```sh
.\venv\Scripts\activate
```
* Install brazfoot_cli dependencies:
```sh
pip install -r requirements.txt
```
* Run brazfoot_cli application:
```sh
python src\main.py
```
* to check the available command options:
```sh
python src\main.py --help
```
* To exit the virtual environment:
```sh
deactivate
```

### [Docker](https://hub.docker.com/r/jrkrauss/brazfoot_cli) setup :whale:

To quickly try this out, download our image and run it following the steps below:

* Change directory:
```sh
cd brazfoot_cli
```
* Build the container
```sh
docker build -t brazfoot_cli .
```
* [ Linux ] Run the container specifying a volume for the resulting json file 
```sh
docker run -it -v $PWD/export:/usr/src/app/export brazfoot_cli
```
* [ Windows ] Run the container specifying a volume for the resulting json file
```sh
docker run -it -v %USERPROFILE%\export:/usr/src/app/export brazfoot_cli

```