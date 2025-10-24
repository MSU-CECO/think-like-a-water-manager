
# ======== Adapted from:  ==== #
# ========              Irrigation Guide by USDA NRCS 1997 ==== #
# ========              Chapter 11: Economic Evaluations ==== #


import sympy as sp
from models.units import Units
from models.definitions_loader import DefinitionsLoader
import os
from envs import ANNOTATION_DEFINITIONS_DIR 



# ============ UNITS ================
ECONOMIC_EVALUATIONS_UNITS = {
    "dimensionless_unit": None,
    "percentage": Units.percentage,
    "dollar": Units.dollar,
    "acreft_per_year": Units.rate_in_acreft_per_year,
    "acres": Units.area_in_acres,
    "kWh": Units.kilowatts_hours,
    "kWh/yr": Units.kilowatts_hours_per_year,
    "ac-in/ac/yr": Units.pressure_in_acre_inch_per_acre_per_year,
    "lb/in²": Units.pressure_in_pounds_per_inch_squared,
    "bu/ac": Units.bushel_per_acre,
}

# ============ SYMBOLS ================


from data.irrigation_system_performance_equations import TIA   # total_irrigated_area


SES = sp.symbols("SES")                         # seasonal_energy_savings (kilowatts-hours/year)
SGIA = sp.symbols("SGIA")                       # seasonal_gross_irrigation_applied (ac-in/ac/yr)
PRAS = sp.symbols("PRAS")                       # pressure_reduction_at_sprinkler (lb/in^2)
PRASC = sp.symbols("PRASC")                     # pressure_reduction_at_sprinkler_currently (lb/in^2)
PRASA = sp.symbols("PRASA")                     # pressure_reduction_at_sprinkler_after_conversion (lb/in^2)
OPPE = sp.symbols("OPPE")                       # overall_pumping_plant_efficiency (dimensionless_unit)

seasonal_energy_savings_expression = sp.Eq(
    SES,
    (TIA * SGIA * (PRASC - PRASA) * 0.2) / (OPPE / 100)
)  

EEC = sp.symbols("EEC")                         # electric_energy_cost (kWh)
DSOEECPY = sp.symbols("DSOEECPY")               # dollars_saved_on_electric_energy_cost_per_year (dollar)
dollars_saved_on_electric_energy_cost_per_year_expression = sp.Eq(
    DSOEECPY,
    SES * EEC
)



UPEI = sp.symbols("UPEI")                           # unit_price_expected_increase (dollar/bushel)
GVPAEIFI = sp.symbols("GVPAEIFI")                   # gross_value_per_acre_expected_increase_from_irrigation (dollar)
gross_value_per_acre_expected_increase_from_irrigation_expression = sp.Eq(
    GVPAEIFI,
    TIA * UPEI
)

TECOIS = sp.symbols("TECOIS")                       # total_estimated_cost_of_irrigation_system (dollar)

OCPY = sp.symbols("OCPY")                           # ownership_cost_per_year (dollar)
IOFCPA = sp.symbols("IOFCPA")                       # increased_ownership_fixed_cost_per_acre (dollar)
increased_ownership_fixed_cost_per_acrem_expression = sp.Eq(
    IOFCPA,
    OCPY / TIA
)

TIOCPA = sp.symbols("TIOCPA")                       # total_increased_operating_costs_per_acre (dollar)
OPCDEP = sp.symbols("OPCDEP")                       # operating_costs_dueto_electricpump (dollar)
OPCDRM = sp.symbols("OPCDRM")                       # operating_costs_dueto_repair_maintenance (dollar)
OPCO = sp.symbols("OPCO")                           # operating_costs_others (dollar)
total_increased_operating_costs_per_acre_expression = sp.Eq(
    TIOCPA,
    OPCDEP + OPCDRM + OPCO
)

TAACIPA = sp.symbols("TAACIPA")                       # total_average_annual_costs_increased_per_acre (dollar)
total_average_annual_costs_increased_per_acre_expression = sp.Eq(
    TAACIPA,
    IOFCPA + TIOCPA
)

EAAINIPA = sp.symbols("EAAINIPA")                       # expected_average_annual_increase_in_net_icome_per_acre (dollar)
expected_average_annual_increase_in_net_icome_per_acre_expression = sp.Eq(
    EAAINIPA,
    GVPAEIFI - TAACIPA
)


# ============ EXPRESSIONS ================
ECONOMIC_EVALUATIONS_EXPRESSIONS = {

    "eq_seasonal_energy_savings": seasonal_energy_savings_expression,
    "eq_dollars_saved_on_electric_energy_cost_per_year": dollars_saved_on_electric_energy_cost_per_year_expression,

    "eq_gross_value_per_acre_expected_increase_from_irrigation": gross_value_per_acre_expected_increase_from_irrigation_expression,
    "eq_increased_ownership_fixed_cost_per_acre": increased_ownership_fixed_cost_per_acrem_expression,
    "eq_total_increased_operating_costs_per_acre": total_increased_operating_costs_per_acre_expression,
    "eq_total_average_annual_costs_increased_per_acre": total_average_annual_costs_increased_per_acre_expression,
    "eq_expected_average_annual_increase_in_net_icome_per_acre": expected_average_annual_increase_in_net_icome_per_acre_expression,

}








# ============ LOADER ================

terms_yaml_path = os.path.join(ANNOTATION_DEFINITIONS_DIR, "economic_evaluations_terms.yaml")
equations_yaml_path = os.path.join(ANNOTATION_DEFINITIONS_DIR, "economic_evaluations_equations.yaml")

# Create loader for soil science domain
economic_evaluations_loader = DefinitionsLoader(
    domain_name="economic_evaluations",
    terms_yaml_path=terms_yaml_path,
    equations_yaml_path=equations_yaml_path,
    units_dict=ECONOMIC_EVALUATIONS_UNITS,
    sympy_expressions=ECONOMIC_EVALUATIONS_EXPRESSIONS
)

ECONOMIC_EVALUATIONS_TERMS = economic_evaluations_loader.load_terms()
ECONOMIC_EVALUATIONS_EQUATIONS = economic_evaluations_loader.load_equations()
