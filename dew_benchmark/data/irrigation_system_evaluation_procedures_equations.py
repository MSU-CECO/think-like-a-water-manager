
# ======== Adapted from:  ==== #
# ========              Irrigation Guide by USDA NRCS 1997 ==== #
# ========              652.0904 Irrigation system evaluation procedures ==== #


import sympy as sp
from models.units import Units
from models.definitions_loader import DefinitionsLoader
import os
from envs import ANNOTATION_DEFINITIONS_DIR 

# ============ UNITS ================
IRRIGATION_SYSTEM_EVALUATION_PROCEDURES_UNITS = {
    "dimensionless_unit": None,
    "percentage": Units.percentage,
    "reference_et_in_mm_per_day_unit": Units.rate_in_mm_per_day,
    "reference_et_in_mm_per_month_unit": Units.rate_in_mm_per_month,
    "water_depth_in_mm_unit": Units.millimeter,
    "celsius": Units.celsius,  
    "days": Units.time_in_days,
    "hours": Units.time_in_hours,
    "dollar": Units.dollar,
    "inches": Units.inches,
    "feet": Units.feet,
    "acreft_per_year": Units.rate_in_acreft_per_year,
    "acres": Units.area_in_acres,
}



# ============ SYMBOLS ================


# for everytihing below, refere to pg 9-55
TID, TIF, NIRF = sp.symbols("TID TIF NIRF")                 # typical_irrigation_duration , typical_irrigation_frequency, number_of_irrigations_for_year
PIEA = sp.symbols("PIEA")                        # present_irrigation_application_efficiency (percent)
from data.irrigation_system_performance_equations import E_a, TIA   # irrigation_application_efficiency, total_irrigated_area
PEGIAPY, PANAPI = sp.symbols("PEGIAPY PANAPI")                      # present_gross_irrigation_applied_per_year (in), present_average_net_application_per_irrigation (in)
present_gross_irrigation_applied_per_year_expression = sp.Eq(
    PEGIAPY,
    (PANAPI * NIRF * 100) / PIEA
)  
PGDA = sp.symbols("PGDA")                 # present_gross_depth_applied (in)
present_gross_irrigation_applied_per_year_using_depth_applied_expression = sp.Eq(
    PEGIAPY,
    PGDA * NIRF
)  

ANIR, PAE = sp.symbols("ANIR PAE")          # annual_net_irrigation_requirement (in), potential_application_efficiency (percent)
POGIAPY = sp.symbols("POGIAPY")             # potential_gross_irrigation_applied_per_year (in)
potential_gross_irrigation_applied_per_year_expression = sp.Eq(
    POGIAPY,
    (ANIR / PAE ) * 100
)  

AFSPY = sp.symbols("AFSPY")                 # acrefeet_saved_per_year (acre-ft/year)
total_annual_water_saved_expression = sp.Eq(
    AFSPY,
    ((PEGIAPY - POGIAPY)) * TIA / 12
)  


TPCPY, FCPAF = sp.symbols("TPCPY FCPAF")        # total_pumping_cost_per_year ($), fuel_cost_per_acre_foot ($/)
total_pumping_cost_per_year_based_on_fuel_expression = sp.Eq(
    TPCPY,
    FCPAF * AFSPY
)  

TWPCPY, CPAF = sp.symbols("TWPCPY CPAF")     # total_water_purchase_cost_per_year ($), cost_per_acre_foot ($/acre-ft)
total_water_purchase_cost_per_year_expression = sp.Eq(
    TWPCPY,
    CPAF * AFSPY
) 

TCSPY = sp.symbols("TCSPY")                 # total_cost_savings_per_year  ($)
total_cost_savings_per_year_based_on_water_and_pumping_expression = sp.Eq(
    TCSPY,
    TPCPY + TWPCPY
) 

FL = sp.symbols("FL")                 # furrow_length 
FS = sp.symbols("FS")                 # furrow_spacing


# ============ EXPRESSIONS ================
IRRIGATION_SYSTEM_EVALUATION_PROCEDURES_EXPRESSIONS = {

    "eq_total_cost_savings_per_year_based_on_water_and_pumping": total_cost_savings_per_year_based_on_water_and_pumping_expression,
    "eq_total_water_purchase_cost_per_year": total_water_purchase_cost_per_year_expression,
    "eq_total_pumping_cost_per_year_based_on_fuel": total_pumping_cost_per_year_based_on_fuel_expression,
    "eq_total_annual_water_saved": total_annual_water_saved_expression,

    "eq_potential_gross_irrigation_applied_per_year": potential_gross_irrigation_applied_per_year_expression,
    "eq_present_gross_irrigation_applied_per_year": present_gross_irrigation_applied_per_year_expression,
    "eq_present_gross_irrigation_applied_per_year_using_depth_applied": present_gross_irrigation_applied_per_year_using_depth_applied_expression,

}







# ============ LOADER ================

terms_yaml_path = os.path.join(ANNOTATION_DEFINITIONS_DIR, "irrigation_system_evaluation_procedures_terms.yaml")
equations_yaml_path = os.path.join(ANNOTATION_DEFINITIONS_DIR, "irrigation_system_evaluation_procedures_equations.yaml")

# Create loader for soil science domain
irrigation_system_evaluation_procedures_loader = DefinitionsLoader(
    domain_name="irrigation_system_evaluation_procedures",
    terms_yaml_path=terms_yaml_path,
    equations_yaml_path=equations_yaml_path,
    units_dict=IRRIGATION_SYSTEM_EVALUATION_PROCEDURES_UNITS,
    sympy_expressions=IRRIGATION_SYSTEM_EVALUATION_PROCEDURES_EXPRESSIONS
)

IRRIGATION_SYSTEM_EVALUATION_PROCEDURES_TERMS = irrigation_system_evaluation_procedures_loader.load_terms()
IRRIGATION_SYSTEM_EVALUATION_PROCEDURES_EQUATIONS = irrigation_system_evaluation_procedures_loader.load_equations()
