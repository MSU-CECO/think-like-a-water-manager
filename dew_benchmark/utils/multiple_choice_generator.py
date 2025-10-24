# utils/multiple_choice_generator.py
import random
import math


class MultipleChoiceGenerator:
    def __init__(self, equations):
        self.equations = equations
    
    def generate_options(self, problem, num_options=3, difficulty='medium'):
        """Generate multiple choice options for target variables"""
        correct_values = problem["gold_solution_final_response"]
        mc_options = {}
        
        # from pprint import pprint
        # pprint("correct_values")
        # pprint(correct_values)

        for var_name, value_data in correct_values.items():
            correct_value = value_data["value"]
            unit = value_data["unit"]
        
            # Check if correct_value is a symbolic expression and convert to float if possible
            if hasattr(correct_value, 'is_Symbol') or hasattr(correct_value, 'args'):
                try:
                    # Try to evaluate the symbolic expression
                    from sympy import sympify, N
                    correct_value = float(N(correct_value))
                except:
                    # If evaluation fails, skip this variable
                    print(f"Warning: Cannot generate distractors for symbolic expression: {correct_value}")
                    continue
            
            
            # Generate distractors (wrong answers)
            distractors = self._generate_distractors(
                var_name, 
                correct_value, 
                num_options - 1,
                difficulty
            )
            
            # Combine correct answer and distractors
            all_options = [{"value": correct_value, "unit": unit, "is_correct": True}]
            for d in distractors:
                all_options.append({"value": d, "unit": unit, "is_correct": False})
            
            # Shuffle options
            random.shuffle(all_options)
            
            # Find the index of the correct answer
            correct_index = next(i for i, opt in enumerate(all_options) if opt["is_correct"])
            
            # Store the options
            mc_options[var_name] = {
                "options": all_options,
                "correct_index": correct_index
            }
        
        return mc_options
    
    def _generate_distractors(self, var_name, correct_value, num_distractors, difficulty):
        """Generate plausible wrong answers based on common mistakes"""
        
        
        # print(f"Generating distractors for {var_name} with correct value {correct_value}")
        
        distractors = []
        
        # List of distractor generation strategies
        strategies = [
            self._inverse_error,
            self._unit_conversion_error,
            self._arithmetic_error,
            self._formula_error,
            self._magnitude_error,
            self._rounding_error
        ]
        
        # Weight strategies based on difficulty
        if difficulty == 'easy': # e.g., More obvious errors
            weights = [0.1, 0.3, 0.3, 0.1, 0.1, 0.1]  
        elif difficulty == 'medium': # Balanced
            weights = [0.2, 0.2, 0.2, 0.2, 0.1, 0.1]  
        else:  # hard ~ more subtle errors
            weights = [0.1, 0.1, 0.2, 0.3, 0.2, 0.1]  
        
        # Generate distractors until we have enough unique ones
        attempts = 0
        while len(distractors) < num_distractors and attempts < 30:
            strategy = random.choices(strategies, weights=weights)[0]
            distractor = strategy(var_name, correct_value)
            
            # Round to reasonable precision
            precision = max(2, len(str(int(correct_value))) - 1)
            distractor = round(distractor, precision)
            
            # Ensure it's unique and not the correct answer
            if (
                distractor not in distractors and 
                abs(distractor - correct_value) > 1e-6 * abs(correct_value)
            ):
                distractors.append(distractor)
            
            attempts += 1
        
        # If we still need more distractors, use generic numerical variations
        while len(distractors) < num_distractors:
            variation = correct_value * random.uniform(0.5, 1.5)
            if variation not in distractors and abs(variation - correct_value) > 1e-6 * abs(correct_value):
                distractors.append(round(variation, 2))
        
        return distractors


    def _inverse_error(self, var_name, correct_value):
        """Error from inverting a formula (e.g., using 1/x instead of x)"""
        if abs(correct_value) < 1e-10:
            return correct_value + random.uniform(0.1, 1.0)
        return 1.0 / correct_value
    
    def _unit_conversion_error(self, var_name, correct_value):
        """Error from using wrong units (simulate by multiplying or dividing by common factors)"""
        conversion_factors = [10, 100, 1000, 60, 3600, 2.54, 2.2, 1000/3600]
        factor = random.choice(conversion_factors)
        return correct_value * factor
    
    def _arithmetic_error(self, var_name, correct_value):
        """Simple arithmetic errors"""
        error_type = random.choice(["add", "subtract", "wrong_decimal"])
        
        if error_type == "add":
            magnitude = 10 ** math.floor(math.log10(abs(correct_value) + 1e-10))
            return correct_value + random.uniform(0.1, 0.5) * magnitude
        elif error_type == "subtract":
            magnitude = 10 ** math.floor(math.log10(abs(correct_value) + 1e-10))
            return max(0, correct_value - random.uniform(0.1, 0.5) * magnitude)
        else:  # wrong_decimal
            str_value = str(correct_value)
            if '.' in str_value:
                parts = str_value.split('.')
                if len(parts[1]) > 1:
                    # Move decimal point
                    shift = random.choice([-1, 1])
                    new_value = float(str_value.replace('.', '')) * (10 ** (shift - len(parts[1])))
                    return new_value
            return correct_value * 10
    
    def _formula_error(self, var_name, correct_value):
        """Using the wrong formula or missing a term"""
        # Simulate a few common formula errors
        return random.choice([
            correct_value + (correct_value ** 0.5),  # Missing a square root term
            correct_value ** 2,                     # Squaring instead of linear
            correct_value * (1 + random.uniform(-0.3, 0.3))  # Missing a coefficient
        ])
    
    def _magnitude_error(self, var_name, correct_value):
        """Order of magnitude error"""
        # Shift by 1-3 orders of magnitude
        shift = random.choice([-3, -2, -1, 1, 2, 3])
        return correct_value * (10 ** shift)
    
    def _rounding_error(self, var_name, correct_value):
        """Premature rounding error in multi-step problems"""
        # Simulate rounded intermediate value
        variation = random.uniform(0.9, 1.1)
        rounded = round(correct_value * variation, 1)
        return rounded