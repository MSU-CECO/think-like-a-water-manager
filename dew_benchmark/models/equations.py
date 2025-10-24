import sympy as sp

class Equation:
    def __init__(self, id, name, latex, sympy_expr, variables, dependencies=None):
        self.id = id
        self.name = name
        self.latex = latex
        self.sympy_expr = sympy_expr
        self.variables = variables
        self.dependencies = dependencies or []
        self.latex = latex if latex is not None else sp.latex(sympy_expr)
    
    def to_dict(self):
        """Convert to dictionary for Neo4j and JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "latex": self.latex,
            "sympy_expr": self.sympy_expr,
            "variables": self.variables,
            "dependencies": self.dependencies
        }
    
    def solve_for(self, target_var, known_values):
        """Solve equation for target variable given known values"""
        # Create symbols for variables
        symbols = {var: sp.Symbol(var) for var in self.variables}
        
        # Get the target symbol
        target_symbol = symbols[target_var]
        
        # If sympy_expr is an equality
        if isinstance(self.sympy_expr, sp.Equality):
            # Solve for target variable
            solutions = sp.solve(self.sympy_expr, target_symbol)
            if not solutions:
                raise ValueError(f"Cannot solve for {target_var}; no solution found.")
            solution_expr = solutions[0]
        else:
            # It's an expression, return as is
            solution_expr = self.sympy_expr
        
        # Substitute known values
        for var, value in known_values.items():
            if var in symbols:
                solution_expr = solution_expr.subs(symbols[var], value)
        
        # Return the evaluated result if possible
        if solution_expr.is_number:
            return float(solution_expr)
        else:
            try:
                return float(solution_expr.evalf())
            except:
                return solution_expr