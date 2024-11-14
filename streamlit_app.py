import streamlit as st

# Define functions at the top to ensure they are available when called

# Function to calculate adjusted distance based on inputs
def calculate_adjusted_distance(distance_to_hole, hole_elevation, wind_speed, wind_direction, power=100, spin=100):
    # Adjust for hole elevation (assume 3 feet of elevation affects roughly 1 yard)
    adjusted_distance = distance_to_hole + hole_elevation / 3

    # Wind adjustment based on speed and direction
    if wind_speed and wind_direction:
        wind_adjustment = (wind_speed / 12) * distance_to_hole
        if is_headwind(wind_direction):
            adjusted_distance += wind_adjustment
        elif is_tailwind(wind_direction):
            adjusted_distance -= wind_adjustment

    # Adjust for power percentage if less than 100%
    if power < 100:
        power_adjustment = (100 - power) / 100 * distance_to_hole
        adjusted_distance += power_adjustment

    # Set a 5-yard range (low to high)
    return {'low': round(adjusted_distance - 2), 'high': round(adjusted_distance + 2)}

# Determines if wind direction is headwind (toward the golfer)
def is_headwind(direction):
    return direction in ["N", "NNW", "NNE", "NW", "NE"]

# Determines if wind direction is tailwind (away from the golfer)
def is_tailwind(direction):
    return direction in ["S", "SSW", "SSE", "SW", "SE"]

# Calculate left/right adjustment based on lie angle and wind
def calculate_adjustment(lie_angle, wind_speed, wind_direction):
    # Parse the lie angle for direction and value
    angle_value = float(lie_angle[:-1]) if lie_angle[:-1].isdigit() else 0
    direction = lie_angle[-1].upper() if lie_angle else ""

    adjustment = 0

    # Adjust left or right based on lie angle direction
    if direction == "L":
        adjustment += angle_value
    elif direction == "R":
        adjustment -= angle_value

    # Wind impact on side adjustment
    if wind_direction and wind_speed:
        if wind_direction in ["W", "WNW", "WSW"]:
            adjustment += wind_speed / 4
        elif wind_direction in ["E", "ENE", "ESE"]:
            adjustment -= wind_speed / 4

    return round(adjustment)

# Streamlit app code starts here

st.title("Trackman Approach Caddy (TAC)")

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
        wind_direction
    )
    st.write(f"Suggested Range: {adjusted_distance['low']} - {adjusted_distance['high']} yards")
    st.write(f"Adjustment: Aim {abs(aim_adjustment)} yards {'left' if aim_adjustment > 0 else 'right'} of the pin")
