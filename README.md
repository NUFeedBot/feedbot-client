# FeedBot

## setup

You may need to include a feedbot key like below in a .env file at the project directory. This key should match the key being used by the feedbot server for the request to be made.

```
FEEDBOT_KEY=...
```

Which is a pre-shared key that will be sent with requests to the feedbot web server. Requests are always authenticated, but this key can instead be passed with the `--key` argument. If both exist, the command line argument will override the environment variable.

You'll also need to install the requests and openai python packages.

Easiest is to set up a virtual environment with:

``` python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## running

TODO: update below for required `--disable-dry-run` parameter.

To run locally, printing to stdout:

``` python
python main.py -d -s test/ex_submission.rkt -j test/ex_spec.json -a test/ex_assign.rkt -c config.json 
```

To post to a server:

``` python
python main.py -s example/ex_submission.rkt -j example/ex_spec.json -a example/ex_assign.rkt -c config.json -r example/ex_results.json -u https://feedbot.dbp.io -k YOUNEEDTOKNOWTHIS 
```

### args

tacking `--src` or `-s` specifies the file to use as student submission

tacking `--spec` or `-j` specifies the file to use as assignment specification (a json file with metadata about how to give feedback on problems)

tacking `--assignment` or `-a` specifies the file to use for the assignment problems (must correspond to metadata provided with `-j`)

tacking `--config` or `-c` specifies the file to use as system & prompt config, defaults to `config.json` in current directory

tacking `--result` or `-r` specifies the file to store output to, and not to print it

tacking `--url` or `-u` specifies the url where results should be sent, in addition to being printed or storing to a local file.

tacking `--key` or `-k` specifies the key that should be used when sending the request. If you don't pass this argument, but do use `--url`, we will look for a `FEEDBOT_KEY` environment variable.

tacking `--problem` or `-p` specifies the (base 0) index of the (single) problem to get feedback on, rather than doing all the problems. Most likely useful during debugging.

tacking `--debug` or `-d` specifies debug more logging than normal

tacking `--email` or `-e` specifies the email address of the submitter (student)

tacking `--disable-dry-run` disables dry run mode, which means that the client will run in "production" mode and make calls to OpenAI.

### gradescope

TBD

### testing

If you have our `feedbot-data` directory in the same directory where this one is, the following commands will print out results:

Note that hw0 is a bit messed up, since it asks for students to do things before
they know how to do them correctly, and as a result, the feedback is also hard
to give.

``` shell
python main.py -s ../feedbot-data/f1-f23-hw0/bad.rkt -a ../feedbot-data/f1-f23-hw0/template.rkt -j ../feedbot-data/f1-f23-hw0/spec.json -c config.json -p 6

python main.py -s ../feedbot-data/f1-f23-hw1/reference.rkt -a ../feedbot-data/f1-f23-hw1/template.rkt -j ../feedbot-data/f1-f23-hw1/spec.json -c config.json -p 0

python main.py -s ../feedbot-data/f1-f23-hw1/reference.rkt -a ../feedbot-data/f1-f23-hw1/template.rkt -j ../feedbot-data/f1-f23-hw1/spec.json -c config.json -p 1

# This relies upon dependencies, otherwise it can complain about Planet being undefined:
python main.py -s ../feedbot-data/f1-f23-hw1/reference.rkt -a ../feedbot-data/f1-f23-hw1/template.rkt -j ../feedbot-data/f1-f23-hw1/spec.json -c config.json -p 3
```

### batch testing

`batch-test.py` can run several possible config files against several submissions for an assignment, and
put the results in a readable HTML format.

The tacks are: \
`-s`, `--submissions` for a FOLDER containing all of the submissions to run on \
`-c`, `--configs` for a FOLDER containing all of the config (json) files to run on \
`-r`, `--results` for a FOLDER to output resulting JSON and HTML files to \
`-a`, `--assignment` for the file with the assignment problems (must correspond with `-j` metadata) \
`-j`, `--spec` for the metadata spec describing the structure of the assignment file \
`-p`, `--problem` for the problem to run on (optional: if left blank will do all problems) \
`-n`, `--count` for the number of times to repeat each prompt (to look at consistency)

