# brazfoot_cli

## _Brazillian Football Web Scrapper CLI_ :brazil: :soccer:

### Description

**brazfoot_cli** is a CLI application written in Python that extracts information about brazillian football competitions and save them as structured file format such as `json`, `xml` and `csv`.

### Setup

**brazfoot_cli** requires [Python 3.9+](https://www.python.org/downloads/).

```sh
# Clone this repository:
$ git clone https://github.com/krauss/brazfoot_cli.git

# Change directory
$ cd brazfoot_cli

# Install brazfoot_cli dependencies
$ pip install -e .

# Run brazfoot_cli application
$ brazfoot_cli
$ brazfoot_cli --help  # to check the available command options 
```

_P.S: After choosing the file format, the application will dump all the files (one per game match) into the **games** folder_