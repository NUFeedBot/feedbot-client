#!/usr/bin/env python3

#!/usr/bin/env python3

import argparse
import json
import requests
import logging
import os
logger = logging.getLogger(__name__)


from starter_checker import submission_uses_starter
from submission import SubmissionTemplate
from assignment import ProblemStatement, AssignmentStatement
from query import construct

from dotenv import load_dotenv
load_dotenv()


def process(assignment_spec_path,
            assignment_template_path,
            submission_path,
            config_path,
            problem_number,
            post_url,
            submitter_email,
            post_key,
            disable_dry_run):
    logger.info("\n\nprocessing submission {} with assignment {} and config {}\n".format(submission_path,assignment_template_path,config_path))

    with open(config_path, 'r') as config:
        config = json.load(config)

        output_lines = []
        if not submission_uses_starter(output_lines, submission_path, assignment_template_path):
            print("\n".join(output_lines))
            sys.exit(42) # TODO: Verify this error code can't come from other places.

        assignment = AssignmentStatement.load(assignment_spec_path, assignment_template_path)
        submission = SubmissionTemplate.load(submission_path)
        if not disable_dry_run:
            dummy_url = "dummy.url.io"
            print(dummy_url)
            return


        output = {}

        parts = construct(assignment, submission, config, problem_number)

        if post_url:
            request_obj = {
                'email': submitter_email,
                'key': post_key,
                'parts': parts
            }

            response = requests.post(post_url + "/submission", json=request_obj)
            if response.status_code == 200:
                url = post_url + "/submission/" + json.loads(response.text)['id']
                print(url)
            else:
                logger.error("Did not post successfully: " + response.text)

        else:
            print(json.dumps(parts, indent=4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='FeedBot client'
    )

    parser.add_argument('-u', '--url')
    parser.add_argument('-s', '--submission', required = True)
    parser.add_argument('-a', '--assignment', required = True)
    parser.add_argument('-j', '--spec', required = True)
    parser.add_argument('-c', '--config', default = "config.json")
    parser.add_argument('-p', '--problem', type=int)
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-e', '--email', default = "")
    parser.add_argument('-k', '--key', default = os.environ.get("FEEDBOT_KEY",""))
    parser.add_argument('--disable-dry-run', action = "store_true", default = False)

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.INFO)

    process(args.spec, args.assignment, args.submission, args.config, args.problem, args.url, args.email, args.key, args.disable_dry_run)
