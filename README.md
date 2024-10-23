Factorio Blueprints
===================

A command line tool to parse and manage blueprint exchange strings from the game **[Factorio](https://www.factorio.com/)**.

![Python3](http://img.shields.io/badge/python-3-blue.svg?v=1)
[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](./LICENSE)

## Usage

### Input

Read a blueprint exchange string from...

* A raw string directly in the command line:

```
./blueprints.py -s 0eNp9kDFrwzAQhf+KuVkqTk1I0ZitQ6eOJRhZPZLD1klIclIT/N8r2RRnaLsI7un0vfd0h24Y0Qfi1HbO9aDumxJBfTyM5Y6M41WOdGY9FC1NHkEBJbQggLUtkx6TszqRYxkNIRuUXpseZgHEn/gFajefBCAnSoQrchmmlkfbYcgLGyxGtN1AfJZWmwsxyuds5V2k4lBCZGAtYMpndghoyP+bIlsvedVDPQGD7jBXgvd196l6TdXNhT6K6kjJXHJOAVcMcTE9NPVuXzfNy/6wtap/Q8vlazf+21QdV0WbRFdsfx7/QZ+/AShRje0=
```

* A file (one exchange string per line):

`./blueprints.py -f ./tests/examples/blueprint_book.txt`

### Parsing

By default the script will parse the blueprint exchange string and print a summary of its contents:

```
$ python ./blueprints.py -f railway.txt
Book: Railway
Version: 1.1.110
Contents:
  #000 Blueprint: Ore Station - In 1-2 train
  #001 Blueprint: Ore Station - Out 1-2 train
  #002 Blueprint: Straight 2-way block
  #003 Blueprint: T for  two-way rails
  #004 Blueprint: Waiting Area for 1-2 trains
```

If the exchange string is a blueprint book, one can select a page a of the book from its index. From the example above, index 3 selects the "T" junction blueprint:

```
$ python ./blueprints.py -f railway.txt --index 3
Blueprint: T for  two-way rails
Version: 1.1.110
```

Finally one can extract the exchange string for the "T" junction blueprint:

```
$ python ./blueprints.py -f railway.txt --index 3 --exchange
0eJylmNtuozAQhl8l8jWuMD6A8xy9W1WrHLyppRQiQtpGVd59TUyzSTyQme1NJAJ8zIznnxn7iy23B7drfd2x+Rdzdec77/Zs/mu4OP6uD29L17K5yFi9eHNsztqF3/LV68LXfO839WLLMrZr9uHNpu4pn+HhJ52xI5tzoZ706ZQltOJC23eBt3nteI9NSXLggBSJpdgbytq3bhXvquyeqW79HPUwT1y8wuoEqy/Y1aF9d+s
RQ4uBmUPuGmrQJEQpqUEDKRXVFnGmrJq6jkHa9/dF/7NpnauvU86vQyDs1Uf7P7Q5vWSsdWvUk+Fj9xbbi8VLv+FuG8xo/Yrvmq0LVtcu+LBsDm2f/IXNtHlJXDFTiyNyalwFiBHEwNrHuScKXPJVkWhAu6haS+wqUrsUzi6uIlLdI2WK1FgzuYjQEvSWKjWYQpVaiYhZhatPvPyuTyMVWFiii3Adp2Z9UipTFwu0BPgAlQg
ouuPwEg9Fi4LrEWiawgVSFXkkFuCyoGUgR+wqU7vQmvhujAhf0Qq5id89Bd2MbvIF3YvQrQjZiQpCK7JpGxpyKX+cnzKnpFLxeL0ktTuBPU6Sp797y0RqGVqKkZkg07Yp70bB6ZFXf9fbHK63Ei1JO+I0YCFRkvBqoDU4EjkgTar/iVyeztHAOqPbVoSCBUMRu1bicio1RW1aiPaiqD0L0V2UJM1cycgFWKmITRBeEmLHgiE
G51wcdME5VxFntiTkJg0QSQ2XwQ3YVqZyUGg5DPMuOKhqtB5i8MECp9EKsBMQ5FYl7pPhnZgmtgI4JOisthMQYlLbH+6RLXaLbMG5RJsfzSVmak2IsrIghHjoAO+wNVoydoJi8ltRPzoJExIeCwxxooJPYwy6U9hryuRBmJGUsnU5Dxt1FC2owVGYQpyiekrIVL86iymowtdr93mupIMn4ekrLwOnO+76K9+5N3Y2YXilAF6
Jf/Dnf6+9+7Y7hGfiZ3vG/OqMNWPbxdIFAnue/Wna2az7aPjH4jjrv70Pt99du499thKqtEVZVZWxoghiHcyQp78K8Sif
```

### Recursion on blueprint books

By default the script only parses the first level of a blueprint book:

```
$ python ./blueprints.py -f squiggles_in_a_book.txt
Book: Squiggles in a Book
Version: 1.1.104
Contents:
  #000 Blueprint Book: Yellow Mining/Smelting (small E-Poles only)
  #001 Blueprint Book: Science!
  #002 Blueprint Book: Malls
```

For blueprint exchange string with multiple levels of books within book, use the `-l` option to set a maximum recursion level higher than 0:

```
$ python ./blueprints.py -f squiggles_in_a_book.txt -l 1
Book: Squiggles in a Book
Version: 1.1.104
Contents:
  #000 Blueprint Book: Yellow Mining/Smelting (small E-Poles only)
    #000 Blueprint: Smelter Array (Small E-Poles)
    #001 Blueprint: Steel Smelterino V1
    #002 Blueprint: Diagonal Miners
    #003 Blueprint Book: Diagonal Mining
  #001 Blueprint Book: Science!
    #000 Blueprint: Automation/Logistic Science (90/m)
    #001 Blueprint: Chemical Science Expanded (90/m)
    #002 Blueprint: Military Science (90/m)
    #003 Blueprint: Production Science (90/m)
    #004 Blueprint: Utility Science (90/m)
    #007 Blueprint: Chemical Science (45/min)
    #010 Blueprint: Labs (pre-space)
  #002 Blueprint Book: Malls
    #000 Blueprint: Logistics Mall
    #001 Blueprint: Ore/Steam Mall
    #002 Blueprint: Power/Circuit/Train Mall
    #003 Blueprint: Power/Circuit/LTN Mall
    #004 Blueprint: Oil/Pipe Mall
    #005 Blueprint: Nuclear Mall
```

### More commands

`python ./blueprints.py --help`

## Module

Import the script as a module with some useful functions:

* Encode/Decode the exchange string
* Parse the blueprint version
* Parse the blueprint name

See the [unit tests](tests/test_blueprints.py) for code examples

## Requirements

* __Python 3.x__: http://www.python.org/download/

Currently there are no packages required. Should the need arise:

`pip install -r requirements.txt`

## Unit Tests

`python -m unittest -v`
