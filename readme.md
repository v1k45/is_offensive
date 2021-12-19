## is_offensive
Python script to find out if a word is offensive using [Dictionary API](https://dictionaryapi.com/).

### Installation

This project requires Python 3.8 to be installed. [Install Python](https://docs.python-guide.org/starting/installation/).

Install using pip:

```
pip3 install https://github.com/v1k45/is_offensive/archive/refs/heads/master.zip
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
*Only 50 words are searched from the file to avoid exhausting API rate limit.*

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
