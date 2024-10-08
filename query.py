import asyncio
import re
import logging
logger = logging.getLogger(__name__)
from validate import validateSubmissionProb, json_has, json_has_or


def construct(assignment, submission, config, problem_number):
    config_msg = config["system"]
    if problem_number is None:
        probs = assignment.problems
    else:
        probs = [assignment.problems[prob]]

    return [construct_prob(assignment, submission, p, config) for p in probs]



def render_path(p):
    return ", ".join(p)

def find_with_path(l, p):
    for r in l:
        if r["path"] == render_path(p.path):
            return r
    return None

def construct_prob(assignment, submission, problem, config):
    try:
        validateSubmissionProb(problem.path, submission)
        code = submission.at(problem.path, True).contents()
        dependencies_code = submission.extract_responses(problem.dependencies)

        return {
            "path" : render_path(problem.path),
            "prompt" : prompt_from_prob(problem, code, assignment, config, dependencies_code),
            "code" : code
        }
    except e:
        logging.exception(e)
        return  {
            "path": render_path(problem.path),
            "prompt": "ERROR",
            "code": "ERROR"
        }


def prompt_from_prob(problem, code, assignment, config, dep_code):
    has_grading_note = (problem.grading_note != "")
    has_dependencies = (dep_code != "")
    has_context = (problem.context.strip() != "")
    has_code = (code.strip() != "")
    prompt = ""

    # system prompt (now here because o1-mini doesn't have system prompts)
    if config["model"] == "o1-mini":
        prompt += config["system"] + "\n\n"

    # general prompt
    prompt += get_prompt_for("general", problem, config)

    # context (i.e. if the instructor provided extra instructions or data definitions at the top of the code)
    if has_context:
        prompt += get_prompt_for("pre_context", problem, config) \
        + f"```\n{problem.context.strip()}\n```" \
        + get_prompt_for("post_context", problem, config)
    
    # the problem statement (for the specific part, i.e. Problem 1D, or Problem 7A)
    prompt += get_prompt_for("pre_statement", problem, config) \
        + f"```\n{problem.statement.strip()}\n```" \
        + get_prompt_for("post_statement", problem, config)
    
    # an additional grading note, if provided in the spec
    if has_grading_note:
        prompt += get_prompt_for("pre_gradenote", problem, config) \
        + f"```\n{problem.grading_note.strip()}\n```" \
        + get_prompt_for("post_gradenote", problem, config)


    # past code from the student, if it is relevant for this problem
    if has_dependencies:
        prompt += get_prompt_for("pre_dependencies", problem, config) \
        + f"```\n{dep_code.strip()}\n```" \
        + get_prompt_for("post_dependencies", problem, config)
    
    # finally, student code
    code = code if has_code else ";; blank response"
    prompt += get_prompt_for("pre_code", problem, config) \
        + f"```\n{code.strip()}\n```" \
        + get_prompt_for("post_code", problem, config)
    
    return prompt

def get_prompt_for(name, problem, config):
    text = config[name]
    for tag in problem.tags:
        if (name + "#" + tag) in config:
            text += config[name + "#" + tag]
    return text
