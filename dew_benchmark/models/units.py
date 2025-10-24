import sympy.physics.units as spu
from sympy.physics.units.util import convert_to

# Define unit categories

POUND = spu.pounds

class Area:
    """See ISM Table 3.1 - Area units"""
    # Basic area units
    square_meter = spu.meter**2
    square_centimeter = spu.centimeter**2
    square_inch = spu.inch**2
    square_foot = spu.foot**2

    # Define acre as a custom unit
    acre = spu.Quantity("acre", abbrev="ac")
    acre.set_global_relative_scale_factor(43560, square_foot)
    
    @classmethod
    def convert(cls, value, from_unit, to_unit):
        """Convert between area units"""
        return convert_to(value * from_unit, to_unit)


class Volume:
    """See ISM Table 3.1 - Volume units"""
    # Basic volume units
    liter = spu.liter
    milliliter = spu.milliliter

    cubic_centimeter = spu.Quantity("cubic_centimeter", abbrev="cm³")
    cubic_centimeter.set_global_relative_scale_factor(1e-6, spu.meter**3)
    
    cubic_meter = spu.Quantity("cubic_meter", abbrev="m³")
    cubic_meter.set_global_relative_scale_factor(1, spu.meter**3)
    
    # Define custom units
    gallon = spu.Quantity("gallon", abbrev="gal")
    gallon.set_global_relative_scale_factor(3.79, liter)


    # Define acre-inch as a custom unit
    acre_inch = spu.Quantity("acre_inch", abbrev="ac-in")
    acre_inch.set_global_relative_scale_factor(27154, gallon)

    ton = spu.Quantity("ton", abbrev="ton")
    ton.set_global_relative_scale_factor(1000, spu.kilogram)

    acre_foot = spu.Quantity("acre_foot", abbrev="ac-ft")
    acre_foot.set_global_relative_scale_factor(2000, ton)

    acreft_per_year = spu.Quantity("acreft_per_year", abbrev="ac-ft/yr")
    acreft_per_year.set_global_relative_scale_factor(1, acre_foot / spu.year)


    
    @classmethod
    def convert(cls, value, from_unit, to_unit):
        """Convert between volume units"""
        return convert_to(value * from_unit, to_unit)


class Flow:
    """See ISM Table 3.1 - Flow units"""

    # Basic flow units
    cubic_meter_per_second = Volume.cubic_meter / spu.second
    liter_per_second = spu.liter / spu.second
    milliliter_per_second = spu.milliliter / spu.second
    feet_per_second = spu.foot / spu.second
    inch_per_hour = spu.inch / spu.hour
    inch_per_day = spu.inch / (spu.day)

    # Define custom units
    gallon_per_minute = spu.Quantity("gallon_per_minute", abbrev="gpm")
    gallon_per_minute.set_global_relative_scale_factor(0.06309, liter_per_second)

    gallon_per_minute_per_acre = spu.Quantity("gallon_per_minute_per_acre", abbrev="gpm/ac")
    gallon_per_minute_per_acre.set_global_relative_scale_factor(1, gallon_per_minute / Area.acre)


    gallon_per_minute_per_feetsquared = spu.Quantity("gallon_per_minute_per_feetsquared", abbrev="gpm/ft²")
    gallon_per_minute_per_feetsquared.set_global_relative_scale_factor(1, gallon_per_minute / Area.square_foot)

    gallon_per_hour = spu.Quantity("gallon_per_hour", abbrev="gal/h")
    gallon_per_hour.set_global_relative_scale_factor(63.1, milliliter_per_second)

    cubic_foot_per_second = spu.Quantity("cubic_foot_per_second", abbrev="cfs")
    cubic_foot_per_second.set_global_relative_scale_factor(0.02832, cubic_meter_per_second)

    acre_inch_per_hour = spu.Quantity("acre_inch_per_hour", abbrev="ac-in/hr")
    acre_inch_per_hour.set_global_relative_scale_factor(1, cubic_foot_per_second)

    feet_cubed_per_hour = spu.Quantity("feet_cubed_per_hour", abbrev="ft³/h")
    feet_cubed_per_hour.set_global_relative_scale_factor(1, spu.foot**3 / spu.hour)
    
    
    @classmethod
    def convert(cls, value, from_unit, to_unit):
        """Convert between flow units"""
        return convert_to(value * from_unit, to_unit)


class Pressure:
    # Basic pressure units
    bar = spu.bar
    pascal = spu.pascal
    psi = spu.psi
    
    # Define centibar (cb) as 0.01 * bar
    centibar = spu.Quantity("centibar", abbrev="cb")
    # Set the global relative scale factor
    centibar.set_global_relative_scale_factor(0.01, bar)
    
    # Kilopascal for convenience
    kilopascal = spu.Quantity("kilopascal", abbrev="kPa")
    kilopascal.set_global_relative_scale_factor(1000, pascal)

    
    @classmethod
    def convert(cls, value, from_unit, to_unit):
        """Convert between pressure units"""
        return convert_to(value * from_unit, to_unit)


class Power:
    """See ISM Table 3.1 - Power units"""
    # Basic power units
    watt = spu.watt

    horsepower_uscs_system = spu.Quantity("horsepower", abbrev="hp")
    # 1 hp = 33,000 ft-lb/min # see Eisenhauer et al. (2021) - Equation 8.17
    horsepower_uscs_system.set_global_relative_scale_factor(33000, spu.foot * spu.pound / spu.minute)
    

    # Define custom units
    kilowatt = spu.Quantity("kilowatt", abbrev="kW")
    kilowatt.set_global_relative_scale_factor(1000, watt)

    
    @classmethod
    def convert(cls, value, from_unit, to_unit):
        """Convert between power units"""
        return convert_to(value * from_unit, to_unit)


# Main Units class
class Units:
    # SI base units
    gram = spu.gram
    kilogram = spu.kilogram
    centimeter = spu.centimeter
    millimeter = spu.millimeter
    meter = spu.meter
    second = spu.second
    percentage = spu.percent
    inches = spu.inch
    hour = spu.hour
    feet = spu.foot

    time_in_days = spu.day
    time_in_hours = spu.hour
    time_in_minutes = spu.minute
    
    # Force units
    newton = spu.newton

    # Power units
    power = Power
    power_in_watt = Power.watt
    power_in_horsepower_uscs_system = Power.horsepower_uscs_system

    # Include pressure units as a nested class
    pressure = Pressure
    pressure_in_bar = Pressure.bar
    pressure_in_centibar = Pressure.centibar
    pressure_in_kilopascal = Pressure.kilopascal
    pressure_in_psi = Pressure.psi
    pressure_in_acre_inch_per_acre_per_year = spu.Quantity("pressure_in_acre_inch_per_acre_per_year", abbrev="ac-in/ac/yr")
    pressure_in_acre_inch_per_acre_per_year.set_global_relative_scale_factor(1, Volume.acre_inch / Area.acre / spu.year)
    pressure_in_pounds_per_inch_squared = spu.Quantity("pressure_in_pounds_per_inch_squared", abbrev="lb/in²")
    pressure_in_pounds_per_inch_squared.set_global_relative_scale_factor(1, spu.pound / spu.inch**2)

    
    # Volume units
    volume = Volume
    volume_in_liter = Volume.liter
    volume_in_gallon = Volume.gallon
    volume_in_acreinches = Volume.acre_inch
    volume_in_cubic_centimeter = Volume.cubic_centimeter
    
    # Area units
    area = Area
    area_in_squarefeet = Area.square_foot
    area_in_squareinches = Area.square_inch
    area_in_acres = Area.acre

    # Flow units
    flow = Flow
    flow_in_gallon_per_minute = Flow.gallon_per_minute
    flow_in_gallon_per_hour = Flow.gallon_per_hour
    flow_in_cubic_foot_per_second = Flow.cubic_foot_per_second
    flow_in_acre_inch_per_hour = Flow.acre_inch_per_hour
    flow_in_acre_inch_per_day = Volume.acre_inch / spu.day
    flow_in_inch_per_hour = Flow.inch_per_hour
    flow_in_feet_per_second = Flow.feet_per_second
    flow_in_inch_per_day = Flow.inch_per_day
    flow_in_feet_cubed_per_hour = Flow.feet_cubed_per_hour

    rate_in_mm_per_day = spu.Quantity("rate_in_mm_per_day", abbrev="mm/day")
    rate_in_mm_per_day.set_global_relative_scale_factor(1, spu.millimeter / spu.day)
    rate_in_mm_per_month = spu.Quantity("rate_in_mm_per_month", abbrev="mm/month")
    rate_in_mm_per_month.set_global_relative_scale_factor(1, spu.millimeter / (spu.day * 30))  # Assuming 30 days in a month
    rate_in_acreft_per_year = Volume.acreft_per_year

    # Energy flux / Irradiance unit
    megajoule_per_square_meter_per_day = (10**6 * spu.joule) / (spu.meter**2 * spu.day)

    kilowatts_hours = spu.Quantity("kilowatts_hours", abbrev="kWh")
    kilowatts_hours.set_global_relative_scale_factor(1, Power.kilowatt * spu.hour)

    kilowatts_hours_per_year = spu.Quantity("kilowatts_hours_per_year", abbrev="kWh/yr")
    kilowatts_hours_per_year.set_global_relative_scale_factor(1, kilowatts_hours / spu.year)

    # Application rate/area-density
    kilogram_per_hectare = spu.kilogram / spu.hectare
    pounds_per_acre = spu.Quantity("pounds_per_acre", abbrev="lb/ac")
    pounds_per_acre.set_global_relative_scale_factor(1.12, kilogram_per_hectare)

    # concentration units
    # see https://efotg.sc.egov.usda.gov/references/Public/NH/Useful_Conversions.pdf
    ton_per_acrefoot = Volume.ton / Volume.acre_foot
    parts_per_million = spu.Quantity("parts_per_million", abbrev="ppm")
    parts_per_million.set_global_relative_scale_factor(735.294, ton_per_acrefoot)

    concentration_in_mg_per_liter = spu.Quantity("concentration_in_mg_per_liter", abbrev="mg/L")
    concentration_in_mg_per_liter.set_global_relative_scale_factor(1, spu.milligram / spu.liter)

    loss_in_acre_feet = Volume.acre_foot
    loss_rate_in_acre_feet_per_year = Volume.acre_foot / spu.year
    loss_rate_in_acre_feet_per_day = Volume.acre_foot / spu.day


    irrigation_length_per_year = spu.day / spu.year
    flow_contact_area_value = spu.feet**2 / spu.feet
    flow_contact_area = spu.Quantity("flow_contact_area", abbrev="ft²/ft")
    flow_contact_area.set_global_relative_scale_factor(1, flow_contact_area_value)

    seepage_loss_rate_value = spu.feet**3 / spu.feet**2 / spu.day
    seepage_loss_rate = spu.Quantity("seepage_loss_rate", abbrev="ft³/ft²/day") 
    seepage_loss_rate.set_global_relative_scale_factor(1, seepage_loss_rate_value)

    wetted_surface_area_per_irrigated_acreage_value = spu.feet**2 / Area.acre
    wetted_surface_area_per_irrigated_acreage = spu.Quantity("wetted_surface_area_per_irrigated_acreage", abbrev="ft²/ac")
    wetted_surface_area_per_irrigated_acreage.set_global_relative_scale_factor(1, wetted_surface_area_per_irrigated_acreage_value)
    
    system_capacity_in_gpm_per_acre = Flow.gallon_per_minute_per_acre
    pressure_loss_in_psi_per_feet = spu.Quantity("pressure_loss_in_psi_per_feet", abbrev="psi/ft")
    pressure_loss_in_psi_per_feet.set_global_relative_scale_factor(1, Pressure.psi / spu.foot)

    flow_rate_per_unit_area_in_gpm_per_feetsquared = Flow.gallon_per_minute_per_feetsquared

    weight_in_tons = Volume.ton

    # Miscellaneous
    electrical_conductivityin_xsiemens_per_m = spu.Quantity("electrical_conductivity", abbrev="dS/m")
    electrical_conductivityin_xsiemens_per_m.set_global_relative_scale_factor(1, spu.siemens / spu.meter)
    
    percent_yield_decline = spu.Quantity("percent_yield_decline", abbrev="%/dS/m")
    percent_yield_decline.set_global_relative_scale_factor(1, spu.percent / electrical_conductivityin_xsiemens_per_m)
    
    weight_of_volume_of_fluid_in_psi_per_feet = spu.Quantity("weight_of_volume_of_fluid_in_psi_per_feet", abbrev="psi/ft")
    weight_of_volume_of_fluid_in_psi_per_feet.set_global_relative_scale_factor(1, spu.psi / spu.foot)

    waterhorsepowerhour_per_energy_of_gallons = spu.Quantity("waterhorsepowerhour_per_energy", abbrev="whp*h/gal")
    waterhorsepowerhour_per_energy_of_gallons.set_global_relative_scale_factor(1, Power.horsepower_uscs_system * spu.hour / Volume.gallon)

    energy_consumed_per_acreinches_of_water = spu.Quantity("energy_consumed_per_acreinches_of_water", abbrev="gal/ac-in")
    energy_consumed_per_acreinches_of_water.set_global_relative_scale_factor(1, Volume.gallon / Volume.acre_inch)

    # Temperature units
    kelvin = spu.kelvin
    celsius = spu.Quantity("celsius", abbrev="°C")
    celsius.set_global_relative_scale_factor(1, kelvin - 273.15)  # Celsius to Kelvin conversion

    # Currency
    dollar = "$"
    bushel_per_acre = "bu/ac"

    @classmethod
    def get_unit(cls, unit_name):
        """Get unit by name"""
        if hasattr(cls, unit_name):
            return getattr(cls, unit_name)
        return None
    
    @classmethod
    def convert(cls, value, from_unit, to_unit):
        """Convert between compatible units"""
        return convert_to(value * from_unit, to_unit)