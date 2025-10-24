# utils/dataset_generator.py
import random
import uuid
from utils.sympy_solver import SympySolver
from utils.multiple_choice_generator import MultipleChoiceGenerator
from envs import (
    DEFAULT_PROBLEM_DIFFICULTY_LEVEL, 
    DEFAULT_NUM_DECIMALS_TO_ROUND_TO,
    DEFAULT_NUM_PROBLEMS_PER_TEMPLATE
)

class DatasetGenerator:
    def __init__(self, neo4j_manager, equations):
        self.neo4j_manager = neo4j_manager
        self.equations = equations
        self.solver = SympySolver(equations)

    def _populate_problem_values(self, problem, template, original_version):
        """
        Populate the problem with values generated from the template.
        
        This function processes each variable defined in the template and assigns 
        appropriate values to the problem. Constants are handled differently from
        regular variables:
        - For original versions, all variables use their minimum values, which are assumed to be the test dataset (i.e., 0-shot).
        - For random versions:
          - Constants use the midpoint between min and max
          - Regular variables use random values within their min-max range
          
        All values are rounded to the default precision defined in envs.
        
        Parameters:
        -----------
        problem : dict
            The problem dictionary to update with variable values
        template : ProblemTemplate 
            The template containing variable definitions
        original_version : bool
            If True, use minimum values; if False, generate random values
            
        Returns:
        --------
        dict
            The updated problem dictionary with populated given_values
        """
        for var_name, var_config in template.variables.items():
            # Determine value based on variable type and version
            is_constant = var_config.get("is_constant", False)
            
            if is_constant:
                # Use midpoint for constants in random versions
                value = (var_config["min"] + var_config["max"]) / 2
            else:
                # Generate random value for non-constants
                value = random.uniform(var_config["min"], var_config["max"])
            
            # Round and store value (keep all in given_values for compatibility)
            problem["given_values"][var_name] = round(value, DEFAULT_NUM_DECIMALS_TO_ROUND_TO)
    
        return problem

    def generate_problem_variation(self, template, variation_id=None, original_version=False):
        """Generate a specific variation of a problem template"""
        if variation_id is None:
            # Generate a unique ID
            variation_id = str(uuid.uuid4())[:8]
        
        # Create a new problem instance
        problem = {
            "id": f"{template.id}_{variation_id}",
            "problem_category": template.problem_category,
            "difficulty_level": template.difficulty_level,
            "citation": template.citation,
            "equations_used": template.equations_used,
            "given_values": {},
            "target_variables": template.target_variables,
            "final_target_variable": template.final_target_variable,
            "additional_references": template.additional_references,
            "manual_hints": template.manual_hints,
            "multiple_choice": template.multiple_choice,
            "is_original_version": original_version,
        }

        problem = self._populate_problem_values(problem, template, original_version)


        if len(template.phrasings) == 0 or "TO_DO" in template.phrasings:
            # If no alternative phrasings, use the base text
            chosen_text = template.problem_text
        else:
            chosen_text = random.choice(template.phrasings)
            
        
        # Fill in the values and units
        formatted_text = chosen_text
        for var_name, value in problem["given_values"].items():
            if var_name in template.variables:
                var_unit = template.variables[var_name].get("default_unit", "")
                formatted_text = formatted_text.replace(f"{{{var_name}}}", str(value))
                formatted_text = formatted_text.replace(f"{{{var_name}_unit}}", var_unit)
        
        problem["gold_problem"] = formatted_text
        return problem
    
    def generate_dataset(self, templates, num_variations_per_template=DEFAULT_NUM_PROBLEMS_PER_TEMPLATE, include_terms=False):
        """Generate a complete dataset from templates"""
        dataset = []

        mc_generator = MultipleChoiceGenerator(self.equations)
        
        for template in templates:
            for i in range(num_variations_per_template):
                
                # make at most one original version per template
                original_version = i == 0

                # Generate problem variation
                problem = self.generate_problem_variation(template, original_version=original_version)
                

                if (
                    "manual_hints" in problem and 
                    problem["manual_hints"].get("override_auto_hints", False)
                ):
                    hints = problem["manual_hints"]["content"]
                else:
                    # Generate hints using Neo4j
                    hints = self.neo4j_manager.get_hints(problem, include_terms)
                
                # Get units mapping for the problem
                units_mapping = self.neo4j_manager.get_variables_with_units()
                
                # Solve the problem
                solution = self.solver.solve_problem(problem=problem, hints=hints, units_map=units_mapping)
                final_target_variable = problem["final_target_variable"][0]
                gold_solution_final_response_solo = {final_target_variable: solution["final_values"][final_target_variable]}

                # Create complete dataset entry
                entry = {
                    "domain_id": problem["id"][:-12],
                    "problem_id": problem["id"],
                    "is_original_version": problem["is_original_version"],
                    "domain": problem["problem_category"][0].replace("_", " "),
                    "topics": problem["problem_category"][1:],
                    "difficulty_level": problem["difficulty_level"],
                    "gold_problem": problem["gold_problem"],
                    "gold_solution_reasoning_steps": solution["steps"],
                    "gold_solution_final_response": gold_solution_final_response_solo,
                    "hint_for_reasoning": hints,
                    "additional_references": problem["additional_references"]
                }

                # Generate multiple choice options based on difficulty
                difficulty = template.difficulty_level if hasattr(template, "difficulty_level") else DEFAULT_PROBLEM_DIFFICULTY_LEVEL
                entry["multiple_choice_options"] = mc_generator.generate_options(
                    entry, 
                    num_options=template.multiple_choice["num_options"], 
                    difficulty=difficulty,
                )
                
                dataset.append(entry)
        
        return dataset