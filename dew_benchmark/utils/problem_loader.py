# utils/problem_loader.py
import os
import json
from models.templates import ProblemTemplate

class ProblemLoader:
    @staticmethod
    def load_from_json(json_obj_or_file):
        """Load problem templates from a JSON file"""

        if isinstance(json_obj_or_file, dict):
            data = json_obj_or_file
        elif os.path.isfile(json_obj_or_file):
            with open(json_obj_or_file, 'r') as f:
                data = json.load(f)
        else:
            raise ValueError(f"Was expecting either a JSON file or a dictionary object, but got: {json_obj_or_file}")
        
        templates = []
        for problem_data in data.get('problems', []):
            # Create template from JSON data
            template = ProblemTemplate(
                template_id=problem_data['id'],
                problem_text=problem_data['problem_text'],
                variables=problem_data['variables'],
                equations_used=problem_data['equations_used'],
                alternative_phrasings=problem_data.get('alternative_phrasings', []),
                problem_category=problem_data.get('problem_category', []),
                difficulty_level=problem_data.get('difficulty_level', 'intermediate'),
                citation=problem_data.get('citation', {}),
                target_variables=problem_data.get('target_variables', []),
                final_target_variable=problem_data.get('final_target_variable', ''),
                additional_references=problem_data.get('additional_references', []),
                manual_hints=problem_data.get('manual_hints', {}),
                multiple_choice=problem_data.get('multiple_choice', {}),
            )
            templates.append(template)
        
        return templates