import sympy as sp
import yaml
from models.equations import Equation
from models.terms import Term
from models.units import Units

class DefinitionsLoader:
    def __init__(self, domain_name, terms_yaml_path, equations_yaml_path, units_dict, sympy_expressions):
        """
        Initialize loader for a specific domain (e.g., soil_science, irrigation)
        
        Args:
            domain_name: Name of the domain (e.g., "soil_water")
            terms_yaml_path: Path to the YAML file containing term definitions
            equations_yaml_path: Path to the YAML file containing equation definitions
            units_dict: Dictionary mapping unit_ids to Unit objects
            sympy_expressions: Dictionary mapping equation_ids to SymPy expressions
        """
        self.domain_name = domain_name
        self.terms_yaml_path = terms_yaml_path
        self.equations_yaml_path = equations_yaml_path
        self.units_dict = units_dict
        self.sympy_expressions = sympy_expressions
        
        # Dictionary to convert unit_ids to human-readable strings
        self.common_unit_strings = {
            unit_id: str(unit) if unit is not None else "dimensionless"
            for unit_id, unit in units_dict.items()
        }
    
    def load_terms(self):
        """Load term definitions from YAML file."""
        try:
            with open(self.terms_yaml_path, 'r') as file:
                terms_data = yaml.safe_load(file)
            
            terms_list = []
            for term_data in terms_data:
                terms_list.append(Term(
                    name=term_data['name'],
                    display_name=term_data['display_name'],
                    symbol=term_data['symbol'],
                    definition=term_data['definition'],
                    common_unit=self.common_unit_strings.get(term_data.get('common_unit_id')),
                    related_terms=term_data.get('related_terms', [])
                ))
            
            return terms_list
        except FileNotFoundError:
            raise FileNotFoundError(f"Terms YAML file not found: {self.terms_yaml_path}")
    
    def load_equations(self):
        """Load equation definitions from YAML file."""
        try:
            with open(self.equations_yaml_path, 'r') as file:
                equations_data = yaml.safe_load(file)
            
            equations_list = []
            for eq_data in equations_data:
                eq_id = eq_data['id']
                if eq_id not in self.sympy_expressions:
                    raise ValueError(f"SymPy expression for equation {eq_id} not defined")
                
                # Process variables
                variables = {}
                for var in eq_data['variables']:
                    var_name = var['name']
                    unit_id = var.get('unit_id')
                    
                    if unit_id is not None and unit_id not in self.units_dict:
                        raise ValueError(f"Unit {unit_id} not defined for variable {var_name} in equation {eq_id}")
                    
                    variables[var_name] = {
                        "description": var['description'],
                        "unit": self.units_dict.get(unit_id)
                    }
                
                equations_list.append(Equation(
                    id=eq_id,
                    name=eq_data['name'],
                    latex=eq_data['latex'],
                    sympy_expr=self.sympy_expressions[eq_id],
                    variables=variables,
                    dependencies=eq_data.get('dependencies', [])
                ))
            
            return equations_list
        except FileNotFoundError:
            raise FileNotFoundError(f"Equations YAML file not found: {self.equations_yaml_path}")