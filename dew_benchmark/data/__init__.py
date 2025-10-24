import importlib
import os
import inspect
from pathlib import Path
from typing import Dict, List, Union

from models.equations import Equation
from models.terms import Term


# Dictionary to store all domain modules
_domain_modules = {}

# Function to dynamically load all domain equation modules from the data directory
def _load_domain_modules():
    # Get the current directory path (data/)
    current_dir = Path(os.path.dirname(__file__))
    
    # Potential domain equation module files (ending with _equations.py)
    potential_modules = [f for f in os.listdir(current_dir) 
                         if f.endswith('_equations.py') and f != '__init__.py']
    
    # Import each domain module and store it
    for module_file in potential_modules:
        module_name = module_file.replace('.py', '')
        domain_name = module_name.replace('_equations', '')
        
        try:
            # Import the module
            full_module_name = f"data.{module_name}"
            module = importlib.import_module(full_module_name)
            
            # Check if it has the expected variables
            terms_var_name = f"{domain_name.upper()}_TERMS"
            equations_var_name = f"{domain_name.upper()}_EQUATIONS"
            
            if hasattr(module, terms_var_name) and hasattr(module, equations_var_name):
                _domain_modules[domain_name] = {
                    'module': module,
                    'terms_var': terms_var_name,
                    'equations_var': equations_var_name
                }
        except ImportError as e:
            print(f"Warning: Could not import module {full_module_name}: {e}")
        except Exception as e:
            print(f"Warning: Error processing module {full_module_name}: {e}")

# Load all domain modules
_load_domain_modules()

# Initialize empty collections
ALL_TERMS: List[Term] = []
ALL_EQUATIONS: List[Equation] = []
TERMS_BY_DOMAIN: Dict[str, List[Term]] = {}
EQUATIONS_BY_DOMAIN: Dict[str, List[Equation]] = {}
TERMS_BY_NAME: Dict[str, Term] = {}
EQUATIONS_BY_ID: Dict[str, Equation] = {}

# Populate collections from loaded modules
for domain_name, module_info in _domain_modules.items():
    module = module_info['module']
    terms_var = getattr(module, module_info['terms_var'])
    equations_var = getattr(module, module_info['equations_var'])
    
    # Add to domain-specific collections
    TERMS_BY_DOMAIN[domain_name] = terms_var
    EQUATIONS_BY_DOMAIN[domain_name] = equations_var
    
    # Add to combined collections
    ALL_TERMS.extend(terms_var)
    ALL_EQUATIONS.extend(equations_var)
    print(f"Loaded {len(terms_var)} terms and {len(equations_var)} equations for domain '{domain_name}'")

# Create lookup dictionaries
TERMS_BY_NAME = {term.name: term for term in ALL_TERMS}
EQUATIONS_BY_ID = {eq.id: eq for eq in ALL_EQUATIONS}

# Helper functions
def get_domain_terms(domain_name: str) -> List[Term]:
    """Get all terms for a specific domain."""
    return TERMS_BY_DOMAIN.get(domain_name, [])

def get_domain_equations(domain_name: str) -> List[Equation]:
    """Get all equations for a specific domain."""
    return EQUATIONS_BY_DOMAIN.get(domain_name, [])

def get_term_by_name(term_name: str) -> Union[Term, None]:
    """Get a term by its name."""
    return TERMS_BY_NAME.get(term_name)

def get_equation_by_id(equation_id: str) -> Union[Equation, None]:
    """Get an equation by its ID."""
    return EQUATIONS_BY_ID.get(equation_id)

def get_available_domains() -> List[str]:
    """Get a list of all available domains."""
    return list(TERMS_BY_DOMAIN.keys())

# Export all collections and helper functions
__all__ = [
    'ALL_TERMS',
    'ALL_EQUATIONS',
    'TERMS_BY_DOMAIN',
    'EQUATIONS_BY_DOMAIN',
    'TERMS_BY_NAME',
    'EQUATIONS_BY_ID',
    'get_domain_terms',
    'get_domain_equations',
    'get_term_by_name',
    'get_equation_by_id',
    'get_available_domains'
]