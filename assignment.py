import json

from submission import SubmissionTemplate, MARKER
from validate import validateJson, validateAssignmentProb, json_has, json_has_or


#Represents a single problem in an assignment along with its metadata
class ProblemStatement:
    def __init__(self, prob_data, template, problem_dependencies):
        self.path = prob_data["path"]
        self.context = self.retrieve_problem_context(template)
        validateAssignmentProb(self.path, template)
        self.statement = template.at(self.path, False).contents()
        self.title = json_has_or(prob_data, "title", str, "") # What is the purpose of title?
        self.stub = json_has_or(prob_data, "stub", str, "")
        self.tags = json_has_or(prob_data, "tags", list, [])
        self.dependencies = problem_dependencies
        self.grading_note = json_has_or(prob_data, "grading_note", str, "")
    
    def retrieve_problem_context(self, template): 
        """
        Returns the context for this problem (instructions in outer problems), given the template
        """

        prob_context = "\n"
        for i in range(1, len(self.path)):
            prob_context += template.at(self.path[0:-i], False).contents()
            prob_context += "\n\n"
        return prob_context
                    
                        





#Represents an entire assignment (a list of problems) along with its metadata
class AssignmentStatement:
    @staticmethod
    def load(spec_path, template_path):
        template = SubmissionTemplate.load(template_path)
        with open(spec_path,'r') as f:
            c = json.load(f)
            c.setdefault('assignment', {})
            return AssignmentStatement(c['assignment'], template)

    def __init__(self, jsondata, template):
        validateJson(jsondata)
        self.title = jsondata["title"]
        self.problems = []

        problem_paths = jsondata["paths"]

        for prob in jsondata["problems"]:
            prob_dependencies = self.get_dependencies(prob, problem_paths)
            prob_statement = ProblemStatement(prob, template, prob_dependencies)
            self.problems.append(prob_statement)
    
    def get_dependencies(self, prob_data, problem_paths):
        """
        Gets all dependencies for given problem.

        Converts all partial dependency paths into final problem paths 
        (ie. [Problem 1] -> [[Problem 1, Part A], [Problem 1, Part B]]

        Throws exception if dependency path is not valid.
        """

        dependencies = json_has_or(prob_data, "dependencies", list, []) #May include partial paths instead of final problems.

        for dep in dependencies:
            #If it is a full path
            if (dep in problem_paths):
                continue

            #Check for partial paths
            is_partial_dependency = False
            for path in problem_paths:

                if path[:len(dep)] == dep:
                    if (not is_partial_dependency):
                        is_partial_dependency = True
                        dependencies.remove(dep)

                    dependencies.append(path)
            
            if (not is_partial_dependency):
                raise InvalidDependencyPath("Problem path is neither a valid partial problem path, nor a complete defined path")
        
        return dependencies




class InvalidDependencyPath(BaseException):
    """Dependency path must be either a defined problem path, or must be a valid partial problem path"""
    def __init__(self, str):
        self.str = str