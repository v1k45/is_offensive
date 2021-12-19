## is_offensive
Python script to find out if a word is offensive using [Dictionary API](https://dictionaryapi.com/).

### Installation

This project requires Python 3.8 to be installed.

Install using pip:

```
pip install https://github.com/v1k45/is_offensive/archive/refs/heads/master.zip
```

### Usage

Setup DictionaryAPI Key:

```
export DICTIONARY_API_KEY=your-api-key
```

Interactive search mode:

```
is_offensive
```

Bulk search using a wordlist file:

```
is_offensive filename.txt
```

### Contributing

This section covers details to setup development environment and start contributing.

Clone repository:
```
git clone git@github.com:v1k45/is_offensive.git
```

Create virtual environment:
```
python3 -m venv venv
. ./venv/bin/activate
```

Setup package for development:
```
python setup.py develop
```

Run tests:
```
python tests.py
```
