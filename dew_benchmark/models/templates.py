# models/templates.py
class ProblemTemplate:
    def __init__(self, template_id, problem_text, variables, equations_used, **kwargs):
        self.id = template_id
        self.problem_text = problem_text
        self.variables = variables
        self.equations_used = equations_used
        self.phrasings = kwargs.get('alternative_phrasings', [])
        self.problem_category = kwargs.get('problem_category', [])
        self.difficulty_level = kwargs.get('difficulty_level', 'intermediate')
        self.citation = kwargs.get('citation', {})
        self.target_variables = kwargs.get('target_variables', [])
        self.final_target_variable = kwargs.get('final_target_variable', [])
        self.additional_references = kwargs.get('additional_references', [])
        self.manual_hints = kwargs.get('manual_hints', {})
        self.multiple_choice = kwargs.get('multiple_choice', {})
    
    def add_phrasing(self, phrasing):
        """Add alternative wording for the same problem"""
        self.phrasings.append(phrasing)
        return self
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "problem_text": self.problem_text,
            "variables": self.variables,
            "equations_used": self.equations_used,
            "alternative_phrasings": self.phrasings,
            "problem_category": self.problem_category,
            "difficulty_level": self.difficulty_level,
            "citation": self.citation,
            "target_variables": self.target_variables,
            "final_target_variable": self.final_target_variable,
            "additional_references": self.additional_references,
            "manual_hints": self.manual_hints,
            "multiple_choice": self.multiple_choice,
        }