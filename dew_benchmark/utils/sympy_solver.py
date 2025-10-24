import sympy as sp
from models.equations import Equation

class SympySolver:
    def __init__(self, equations):
        """Initialize with equations (either as Equation objects or dictionaries)"""
        self.equations = {}
        
        # Handle both Equation objects and dictionaries
        for eq in equations:
            if isinstance(eq, dict):
                # Convert dictionary to Equation object if necessary
                eq_id = eq["id"]
                self.equations[eq_id] = eq
            else:
                # Already an Equation object
                self.equations[eq.id] = eq


    def solve_problem(self, problem, hints=None, units_map=None):
        """
        Use SymPy to solve the problem with given values, optionally using provided hints
        
        Parameters:
        - problem: Dictionary containing problem definition with 'equations_used', 
                'given_values', 'constants', and 'target_variables'
        - hints: Optional hints from Neo4jManager containing the solution path
        
        Returns: Dictionary with solution steps and final values
        """
        # Get relevant equations for this problem
        relevant_eqs = {eq_id: self.equations[eq_id] 
                    for eq_id in problem["equations_used"]}
        
        # Get the values we know
        known_values = dict(problem["given_values"])
        if "constants" in problem:
            known_values.update(problem["constants"])
            
        target_vars = problem["target_variables"]
        
        # Create a dictionary to store the solutions
        solutions = {}
        solution_steps = []
    
        # Add symbol mapping for subscript notation
        symbol_mapping = {
            "theta_fc": sp.Symbol("theta_{fc}"),
            "theta_wp": sp.Symbol("theta_{wp}")
        }
        
        # Create SymPy symbols for our variables
        variables = {}
        for eq_id, eq_data in relevant_eqs.items():
            # Handle both dictionary and Equation objects
            if isinstance(eq_data, dict):
                var_list = eq_data["variables"]
                # Extract variable names from the variables list
                for var_info in var_list:
                    var_name = var_info["name"] if isinstance(var_info, dict) else var_info
                    if var_name not in variables:
                        variables[var_name] = sp.Symbol(var_name)
            else:
                # Equation object
                for var_name in eq_data.variables:
                    if var_name not in variables:
                        variables[var_name] = sp.Symbol(var_name)
        
        # Track which variables we've already solved for
        solved_vars = set(known_values.keys())
        
        # Use solution path if provided by hints, otherwise determine our own
        solution_path = []
        if hints and "solution_path" in hints:
            solution_path = hints["solution_path"]
        else:
            # Simplified approach - for each target variable, find an equation that can solve for it
            for target_var in target_vars:
                for eq_id, eq_data in relevant_eqs.items():
                    eq_vars = []
                    
                    if isinstance(eq_data, dict):
                        eq_vars = [var_info["name"] if isinstance(var_info, dict) else var_info 
                                for var_info in eq_data["variables"]]
                    else:
                        eq_vars = eq_data.variables
                    
                    if target_var in eq_vars:
                        solution_path.append({
                            "target": target_var,
                            "equations": [eq_id]
                        })
                        break
        
        # Now solve each target in the solution path
        for step_counter, step in enumerate(solution_path, 1):
            target_var = step["target"]
            eq_choices = step["equations"]
            
            if target_var in solved_vars:
                # We've already solved for this variable
                continue
            
            # Try each equation until we can solve for the target
            for eq_id in eq_choices:
                eq_data = relevant_eqs[eq_id]
                try:
                    # Get the equation object or create one if needed
                    equation = eq_data
                    if isinstance(eq_data, dict):
                        # Create proper Equation object from dictionary using helper method
                        equation = self._create_equation_from_dict(eq_data)
                    
                    # Filter known_values to only include variables used in this equation
                    current_known_values = {var: value for var, value in known_values.items() 
                                        if var in equation.variables}
                    
                    # Solve for the target variable
                    solution = equation.solve_for(target_var, current_known_values)
                    
                    # Store the solution
                    solutions[target_var] = solution
                    solved_vars.add(target_var)
                    known_values[target_var] = solution
                    
                    # Create step text
                    unit_text = self._get_unit_for_variable(target_var, units_map)
                    
                    step_text = f"Step #{step_counter}: Using equation {equation.name if hasattr(equation, 'name') else eq_id}\n"
                    latex = equation.latex if hasattr(equation, 'latex') else ""
                    if latex:
                        step_text += f"Equation: {latex}\n"
                    
                    # Add substitution details with rounded values
                    step_text += "Substituting: "
                    for var, value in current_known_values.items():
                        formatted_value = self._format_value(value)
                        step_text += f"{var} = {formatted_value}, "
                    step_text = step_text.rstrip(", ") + "\n"
                    
                    # Add result with rounded value
                    formatted_solution = self._format_value(solution)
                    step_text += f"Result: {target_var} = {formatted_solution} {unit_text}\n"
                    solution_steps.append(step_text)
                    
                    # We've solved for this variable, no need to try other equations
                    break
                    
                except Exception as e:
                    print(f"Warning: Could not solve for {target_var} using equation {eq_id}: {e}")
                    # Try the next equation if available
        
        # Format the final response with rounded values
        from envs import DEFAULT_NUM_DECIMALS_TO_ROUND_TO
        precision = problem.get("precision", DEFAULT_NUM_DECIMALS_TO_ROUND_TO)
        final_values = {}
        for var in target_vars:
            if var in solutions:
                unit = self._get_unit_for_variable(var, units_map)
                
                # Get the solution value
                value = solutions[var]
                
                # Round floating point values to specified precision
                if isinstance(value, float):
                    # For values very close to integers, convert to int
                    if abs(value - round(value)) < 1e-10:
                        value = int(round(value))
                    else:
                        # Round to specified precision
                        value = round(value, precision)
                
                final_values[var] = {"value": value, "unit": unit}
        
        return {"steps": solution_steps, "final_values": final_values}


    def _create_equation_from_dict(self, eq_data):
        """
        Create an Equation object from a dictionary representation
        
        Parameters:
        - eq_data: Dictionary containing equation data
        
        Returns: Equation object
        """
        try:
            # Extract the necessary data from the dictionary
            eq_id = eq_data.get("id", "unknown")
            name = eq_data.get("name", eq_id)
            latex = eq_data.get("latex", "")
            
            # Handle variables with different possible structures
            variables = []
            for var_info in eq_data.get("variables", []):
                if isinstance(var_info, dict):
                    # If it's a dictionary, extract the name
                    var_name = var_info.get("name")
                    if var_name:
                        variables.append(var_name)
                elif isinstance(var_info, str):
                    # If it's a string, use it directly
                    variables.append(var_info)
            
            # Extract dependencies if present
            dependencies = eq_data.get("dependencies", [])
            
            # Create the Equation object with appropriate parameters
            try:
                # Try with all parameters first
                return Equation(
                    id=eq_id,
                    name=name,
                    latex=latex,
                    variables=variables,
                    dependencies=dependencies
                )
            except (TypeError, ValueError):
                # If that fails, try with just the essential parameters
                return Equation(eq_id, name, latex, variables)
                
        except Exception as e:
            # If all else fails, create a minimal equation with available data
            print(f"Warning: Error creating Equation object: {e}")
            available_vars = []
            try:
                # Try to extract variable names, even if format is unexpected
                for var_info in eq_data.get("variables", []):
                    if isinstance(var_info, dict) and "name" in var_info:
                        available_vars.append(var_info["name"])
                    elif isinstance(var_info, str):
                        available_vars.append(var_info)
            except Exception:
                pass  # If we can't extract variables, use empty list
                
            return Equation(
                eq_data.get("id", "unknown"),
                eq_data.get("name", "Unknown Equation"),
                eq_data.get("latex", ""),
                available_vars
            )

    def _format_value(self, value, precision=None):
        """
        Format a value with appropriate precision
        
        Parameters:
        - value: The value to format
        - precision: Number of decimal places (if None, uses system default)
        
        Returns: Formatted value as string or original value
        """
        if precision is None:
            # Import default precision from envs
            from envs import DEFAULT_NUM_DECIMALS_TO_ROUND_TO
            precision = DEFAULT_NUM_DECIMALS_TO_ROUND_TO
            
        try:
            # Handle sympy expressions
            if hasattr(value, 'evalf'):
                value = float(value.evalf())
                
            # Handle regular floats
            if isinstance(value, float):
                # Check if it's very close to an integer
                if abs(value - round(value)) < 1e-10:
                    return str(int(round(value)))
                # Otherwise round to specified precision
                return str(round(value, precision))
                
            # Handle fractions
            if hasattr(value, 'numerator') and hasattr(value, 'denominator'):
                if value.denominator == 1:
                    return str(value.numerator)
                # For non-integer fractions, convert to decimal and round
                decimal_val = float(value.numerator) / float(value.denominator)
                if abs(decimal_val - round(decimal_val)) < 1e-10:
                    return str(int(round(decimal_val)))
                return str(round(decimal_val, precision))
                
            # Return original value if not a number
            return str(value)
            
        except Exception:
            # If formatting fails, just return the string representation
            return str(value)

    def _get_unit_for_variable(self, var_name, units_map):
        """Helper to determine the appropriate unit for a variable
        """
        return units_map.get(var_name, "")
        

