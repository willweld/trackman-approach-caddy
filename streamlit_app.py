import math
import streamlit as st

# Define functions at the top to ensure they are available when called

# Function to calculate adjusted distance based on inputs
def calculate_adjusted_distance(distance_to_hole, hole_elevation, wind_speed, wind_direction, power=100):
    # Adjust for hole elevation (assume 3 feet of elevation affects roughly 1 yard)
    adjusted_distance = distance_to_hole + hole_elevation / 3

    # Wind adjustment based on speed and direction
    if wind_speed and wind_direction:
        if is_headwind(wind_direction):
            wind_adjustment = (wind_speed * 0.01) * distance_to_hole  # Add 1% per mph
            adjusted_distance += wind_adjustment
        elif is_tailwind(wind_direction):
            wind_adjustment = (wind_speed * 0.005) * distance_to_hole  # Subtract 0.5% per mph
            adjusted_distance -= wind_adjustment

    # Adjust for power percentage if less than 100%
    if power < 100:
        power_adjustment = (100 - power) / 100 * distance_to_hole
        adjusted_distance += power_adjustment

    # Set a 5-yard range (low to high)
    return {'low': round(adjusted_distance - 2), 'high': round(adjusted_distance + 2)}

# Determines if wind direction is headwind (toward the golfer)
def is_headwind(direction):
    return direction in ["S", "SSW", "SSE", "SW", "SE"]

# Determines if wind direction is tailwind (away from the golfer)
def is_tailwind(direction):
    return direction in ["N", "NNW", "NNE", "NW", "NE"]

# Calculate crosswind component
def calculate_crosswind(wind_speed, wind_direction, shot_direction=0):
    """
    Calculates the crosswind component based on wind speed and relative wind angle.
    :param wind_speed: Wind speed in mph
    :param wind_direction: Wind direction in degrees (0° = North, 90° = East, etc.)
    :param shot_direction: Shot direction in degrees (default is 0°, straight to pin)
    :return: Crosswind component in mph
    """
    wind_degrees = wind_direction_to_degrees(wind_direction)
    relative_angle = (wind_degrees - shot_direction + 360) % 360  # Normalize angle to [0, 360)
    crosswind = abs(wind_speed * math.sin(math.radians(relative_angle)))
    return round(crosswind, 2)

# Map wind direction to degrees
def wind_direction_to_degrees(direction):
    wind_directions = {
        "N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5, "E": 90, "ESE": 112.5,
        "SE": 135, "SSE": 157.5, "S": 180, "SSW": 202.5, "SW": 225, "WSW": 247.5,
        "W": 270, "WNW": 292.5, "NW": 315, "NNW": 337.5
    }
    return wind_directions.get(direction, 0)

# Calculate left/right adjustment based on lie angle, crosswind, and distance
def calculate_adjustment(lie_angle, wind_speed, wind_direction, distance_to_hole):
    # Parse the lie angle for direction and value
    if lie_angle:
        angle_value = float(lie_angle[:-1]) if lie_angle[:-1].isdigit() else 0
        direction = lie_angle[-1].upper()
    else:
        angle_value = 0
        direction = ""

    adjustment = 0

    # Lie angle adjustment based on slope direction and degree
    if direction == "L":
        adjustment -= angle_value * (distance_to_hole / 100)  # Aim right
    elif direction == "R":
        adjustment += angle_value * (distance_to_hole / 100)  # Aim left

    # Crosswind adjustment
    crosswind = calculate_crosswind(wind_speed, wind_direction)
    adjustment += crosswind * (distance_to_hole / 200)  # Crosswind scales with distance

    return round(adjustment)

# Streamlit app code starts here

st.title("GolfSim Approach Caddy")

# Define possible wind directions
wind_directions = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
]

# Form setup
with st.form(key="shot_calc", clear_on_submit=False):
    # Collect initial inputs
    course_elevation = st.number_input("Course Elevation (ft):", value=0.0)
    distance_to_hole = st.number_input("Distance to Hole (yds):", value=0.0)
    hole_elevation = st.number_input("Hole Elevation (ft, +/-):", value=0.0)
    lie_angle = st.text_input("Lie Angle (e.g., '10L' or '5R'):")  # Adding lie angle input
    wind_speed = st.number_input("Wind Speed (mph):", value=0.0)
    wind_direction = st.selectbox("Wind Direction:", wind_directions)
    power = st.number_input("Power % (defaults to 100% if blank):", min_value=0.0, max_value=100.0, value=100.0)    
    submit_button = st.form_submit_button(label="Calculate Shot")

# Display results if the form is submitted
if submit_button:
    adjusted_distance = calculate_adjusted_distance(
        distance_to_hole,
        hole_elevation,
        wind_speed,
        wind_direction,
        power
    )
    aim_adjustment = calculate_adjustment(
        lie_angle,
        wind_speed,
        wind_direction,
        distance_to_hole
    )
    crosswind = calculate_crosswind(wind_speed, wind_direction)
    st.write(f"Suggested Distance: {adjusted_distance['low']} - {adjusted_distance['high']} yards")
    st.write(f"Crosswind Component: {crosswind} mph")
    st.write(f"Adjustment: Aim {abs(aim_adjustment)} yards {'left' if aim_adjustment > 0 else 'right'} of the pin")
