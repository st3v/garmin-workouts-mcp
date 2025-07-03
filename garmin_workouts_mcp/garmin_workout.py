from typing import List, Tuple


# Sport type mapping
SPORT_TYPE_MAPPING = {
    "running": {"sportTypeId": 1, "sportTypeKey": "running", "displayOrder": 1},
    "cycling": {"sportTypeId": 2, "sportTypeKey": "cycling", "displayOrder": 2},
    "swimming": {"sportTypeId": 4, "sportTypeKey": "swimming", "displayOrder": 5},
    "strength": {"sportTypeId": 5, "sportTypeKey": "strength_training", "displayOrder": 9},
    "cardio": {"sportTypeId": 6, "sportTypeKey": "cardio_training", "displayOrder": 8},
}

# Step type mapping
STEP_TYPE_MAPPING = {
    "warmup": {"stepTypeId": 1, "stepTypeKey": "warmup", "displayOrder": 1},
    "cooldown": {"stepTypeId": 2, "stepTypeKey": "cooldown", "displayOrder": 2},
    "interval": {"stepTypeId": 3, "stepTypeKey": "interval", "displayOrder": 3},
    "recovery": {"stepTypeId": 4, "stepTypeKey": "recovery", "displayOrder": 4},
    "rest": {"stepTypeId": 5, "stepTypeKey": "rest", "displayOrder": 5},
    "repeat": {"stepTypeId": 6, "stepTypeKey": "repeat", "displayOrder": 6},
}

# Target type mapping
TARGET_TYPE_MAPPING = {
    "no target": {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target", "displayOrder": 1},
    "power": {"workoutTargetTypeId": 2, "workoutTargetTypeKey": "power.zone", "displayOrder": 2},
    "cadence": {"workoutTargetTypeId": 3, "workoutTargetTypeKey": "cadence.zone", "displayOrder": 3},
    "heart rate": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone", "displayOrder": 4},
    "speed": {"workoutTargetTypeId": 5, "workoutTargetTypeKey": "speed.zone", "displayOrder": 5},
    "pace": {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone", "displayOrder": 6},
}

# Distance unit mapping
DISTANCE_UNIT_MAPPING = {
    "m": {"unitId": 2, "unitKey": "m", "factor": 1},
    "km": {"unitId": 3, "unitKey": "km", "factor": 1000},
    "mile": {"unitId": 4, "unitKey": "mile", "factor": 1609.344},
}

# End condition type mapping
END_CONDITION_TYPE_MAPPING = {
    "time": {"conditionTypeId": 2, "conditionTypeKey": "time", "displayOrder": 2, "displayable": True},
    "distance": {"conditionTypeId": 3, "conditionTypeKey": "distance", "displayOrder": 3, "displayable": True},
    "lap.button": {"conditionTypeId": 1, "conditionTypeKey": "lap.button", "displayOrder": 1, "displayable": True},
    "iterations": {"conditionTypeId": 7, "conditionTypeKey": "iterations", "displayOrder": 7, "displayable": False},
}

# Default pace values in seconds per meter for different sport types
DEFAULT_PACE = {
    "running": 0.36,      # ~6:00 min/km or ~9:40 min/mile
    "cycling": 0.05,      # ~3:00 min/km or ~5:00 min/mile (12 mph)
    "swimming": 0.5,      # ~8:20 min/100m
    "walking": 0.3,       # ~5:00 min/km
    "strength": 0.36,     # Same as running
    "cardio": 0.36,       # Same as running
}


def make_payload(workout: dict) -> dict:
    """
    Main function to create the workout payload.

    Args:
        workout: The workout object containing workout details and steps

    Returns:
        The formatted payload ready to be sent to Garmin
    """
    step_order = 1
    sport_type = get_sport_type(workout["type"])
    payload = {
        "sportType": sport_type,
        "subSportType": None,
        "workoutName": workout["name"],
        "estimatedDistanceUnit": {
            "unitKey": None,
        },
        "workoutSegments": [],
        "avgTrainingSpeed": None,
        "estimatedDurationInSecs": 0,
        "estimatedDistanceInMeters": 0,
        "estimateType": None,
    }

    segment = {
        "segmentOrder": 1,
        "sportType": sport_type,
        "workoutSteps": [],
    }

    result = process_steps(workout["steps"], step_order)
    segment["workoutSteps"] = result["steps"]
    step_order = result["stepOrder"]

    payload["workoutSegments"].append(segment)
    payload["estimatedDurationInSecs"] = calculate_estimated_duration(payload["workoutSegments"])

    return payload


def get_sport_type(sport_type_key: str) -> dict:
    """
    Retrieves the sport type object from the mapping.

    Args:
        sport_type_key: The sport type key (e.g., 'running')

    Returns:
        The sport type object

    Raises:
        ValueError: If sport type is not supported
    """
    sport_type = SPORT_TYPE_MAPPING.get(sport_type_key.lower())
    if not sport_type:
        raise ValueError(f"Unsupported sport type: {sport_type_key}")
    return sport_type


def process_steps(steps_array: List[dict], step_order: int) -> dict:
    """
    Recursively processes an array of steps.

    Args:
        steps_array: The array of steps to process
        step_order: The current step order

    Returns:
        An object containing the array of formatted steps and updated stepOrder
    """
    steps = []

    for step in steps_array:
        result = process_step(step, step_order)
        steps.append(result["step"])
        step_order = result["stepOrder"]

    return {"steps": steps, "stepOrder": step_order}


def process_step(step: dict, step_order: int) -> dict:
    """
    Processes an individual step (regular or repeat).

    Args:
        step: The step object to process
        step_order: The current step order

    Returns:
        An object containing the formatted step and updated stepOrder
    """
    # Handle both stepType and endConditionType for identifying repeat steps
    if (step.get("numberOfIterations") and step.get("steps") and
        (step.get("stepType") == "repeat" or step.get("endConditionType") == "repeat")):
        return process_repeat_step(step, step_order)
    elif not step.get("stepType"):
        raise ValueError(f"Missing stepType for step: {step.get('stepName', 'Unnamed Step')}")
    else:
        return process_regular_step(step, step_order)


def process_regular_step(step: dict, step_order: int) -> dict:
    """
    Processes a regular executable step.

    Args:
        step: The step object to process
        step_order: The current step order

    Returns:
        An object containing the formatted executable step and updated stepOrder
    """
    step_type = STEP_TYPE_MAPPING.get(step["stepType"].lower(), STEP_TYPE_MAPPING["interval"])

    workout_step = {
        "stepId": step_order,
        "stepOrder": step_order,
        "stepType": step_type,
        "type": "ExecutableStepDTO",
        "description": step.get("stepDescription", ""),
        "stepAudioNote": None
    }

    # Process end condition (time or distance)
    if (step.get("endConditionType") == "distance" and
        step.get("stepDistance") and step.get("distanceUnit")):
        distance_unit = DISTANCE_UNIT_MAPPING.get(step["distanceUnit"].lower())
        if not distance_unit:
            raise ValueError(f"Unsupported distance unit: {step['distanceUnit']}")

        workout_step["endCondition"] = END_CONDITION_TYPE_MAPPING["distance"]
        workout_step["endConditionValue"] = step["stepDistance"] * distance_unit["factor"]  # Convert to meters

        # When using km for distances >= 1000m, or miles for imperial, make sure
        # the input value is preserved in the native unit rather than being converted
        if distance_unit["unitKey"] == "km" and workout_step["endConditionValue"] >= 1000:
            workout_step["endConditionValue"] = round(workout_step["endConditionValue"])
        elif distance_unit["unitKey"] == "mile":
            # For miles, preserve the exact conversion factor
            workout_step["endConditionValue"] = step["stepDistance"] * 1609.344
    else:
        # Default to time-based
        if not isinstance(step.get("stepDuration"), (int, float)) or step["stepDuration"] <= 0:
            raise ValueError(f"Invalid or missing stepDuration for step: {step.get('stepName', 'Unnamed Step')}")

        workout_step["endCondition"] = END_CONDITION_TYPE_MAPPING["time"]
        workout_step["endConditionValue"] = step["stepDuration"]  # Duration in seconds

    if step.get("target"):
        process_target(workout_step, step)
    else:
        workout_step["targetType"] = TARGET_TYPE_MAPPING["no target"]

    # Explicitly set targetValueUnit to null as seen in the valid payload
    if (workout_step.get("targetType") and
        workout_step["targetType"]["workoutTargetTypeKey"] != "no.target"):
        workout_step["targetValueUnit"] = None

    step_order += 1
    return {"step": workout_step, "stepOrder": step_order}


def process_repeat_step(step: dict, step_order: int) -> dict:
    """
    Processes a repeat step and its child steps.

    Args:
        step: The repeat step object to process
        step_order: The current step order

    Returns:
        An object containing the formatted repeat step and updated stepOrder
    """
    if not isinstance(step.get("numberOfIterations"), int) or step["numberOfIterations"] <= 0:
        raise ValueError("Invalid or missing numberOfIterations for repeat step.")

    repeat_step = {
        "stepId": step_order,
        "stepOrder": step_order,
        "stepType": STEP_TYPE_MAPPING["repeat"],
        "numberOfIterations": step.get("numberOfIterations", 1),
        "smartRepeat": False,
        "endCondition": {
            "conditionTypeId": 7,
            "conditionTypeKey": "iterations",
            "displayOrder": 7,
            "displayable": False,
        },
        "type": "RepeatGroupDTO",
    }

    step_order += 1

    # Recursively process child steps
    result = process_steps(step["steps"], step_order)
    repeat_step["workoutSteps"] = result["steps"]
    step_order = result["stepOrder"]

    return {"step": repeat_step, "stepOrder": step_order}


def process_target(workout_step: dict, step: dict) -> None:
    """
    Processes the target information for a workout step.

    Args:
        workout_step: The workout step object to update
        step: The original step object containing target information
    """
    target_type_key = step["target"]["type"].lower()
    target_type = TARGET_TYPE_MAPPING.get(target_type_key)

    if not target_type:
        raise ValueError(f"Unsupported target type: {step['target']['type']}")

    workout_step["targetType"] = target_type

    if step["target"].get("value"):
        target_values = convert_target_values(step, target_type_key)
        workout_step["targetValueOne"] = target_values["targetValueOne"]
        workout_step["targetValueTwo"] = target_values["targetValueTwo"]


def convert_target_values(step: dict, target_type_key: str) -> dict:
    """
    Converts target values based on the target type and units.

    Args:
        step: The step object containing target values and units
        target_type_key: The target type key (e.g., 'pace')

    Returns:
        An object containing converted target values
    """
    if isinstance(step["target"]["value"], list):
        min_value, max_value = step["target"]["value"]
    else:
        min_value, max_value = calculate_value_range(step["target"]["value"], target_type_key)

    target_value_one = convert_value_to_unit(min_value, step["target"].get("unit"))
    target_value_two = convert_value_to_unit(max_value, step["target"].get("unit"))

    if target_value_one > target_value_two:
        target_value_one, target_value_two = target_value_two, target_value_one

    return {"targetValueOne": target_value_one, "targetValueTwo": target_value_two}


def calculate_value_range(value: float, target_type_key: str) -> Tuple[float, float]:
    """
    Calculates the value range for a target based on the target type.

    Args:
        value: The target value
        target_type_key: The target type key (e.g., 'pace')

    Returns:
        A tuple containing the min and max values for the target range
    """
    if target_type_key == "pace":
        return calculate_pace_range(value)
    return (value * 0.95, value * 1.05)


def calculate_pace_range(pace: float) -> Tuple[float, float]:
    """
    Calculates the pace range based on the target pace.

    Args:
        pace: The target pace in min/km

    Returns:
        A tuple containing the min and max pace values
    """
    ten_seconds_in_minutes = 10 / 60

    min_pace = pace - ten_seconds_in_minutes
    max_pace = pace + ten_seconds_in_minutes

    return (min_pace, max_pace)


def convert_value_to_unit(value: float, unit: str) -> float:
    """
    Converts a value to a specific unit.

    Args:
        value: The value to convert
        unit: The unit to convert to

    Returns:
        The converted value
    """
    if unit == "min_per_km":
        # Convert from min/km to m/s
        # value is in minutes per km, we need meters per second
        # 1 km = 1000m, so if it takes 'value' minutes to run 1000m
        # speed in m/s = 1000 / (value * 60)
        return 1000 / (value * 60)
    return value


def calculate_estimated_duration(workout_segments: List[dict]) -> int:
    """
    Calculates the estimated duration of a workout based on its segments and steps.

    Args:
        workout_segments: The array of workout segments to calculate the duration for

    Returns:
        The estimated duration of the workout in seconds
    """
    duration = 0
    sport_type = workout_segments[0]["sportType"]["sportTypeKey"] if workout_segments else "running"

    for segment in workout_segments:
        for step in segment["workoutSteps"]:
            if step["type"] == "ExecutableStepDTO":
                if step["endCondition"]["conditionTypeKey"] == "distance":
                    # For distance-based steps, estimate duration based on pace
                    duration += estimate_step_duration(step, sport_type)
                else:
                    # For time-based steps, use the step duration directly
                    duration += step["endConditionValue"]
            elif step["type"] == "RepeatGroupDTO":
                # Create a fake segment containing just the child steps of the repeat
                child_steps_duration = calculate_steps_duration(step["workoutSteps"], sport_type)
                duration += step["numberOfIterations"] * child_steps_duration

    return int(duration)


def calculate_steps_duration(steps: List[dict], sport_type: str) -> int:
    """
    Calculates the duration for an array of steps.

    Args:
        steps: The array of steps to calculate the duration for
        sport_type: The sport type key (e.g., 'running')

    Returns:
        The estimated duration in seconds
    """
    duration = 0

    for step in steps:
        if step["type"] == "ExecutableStepDTO":
            if step["endCondition"]["conditionTypeKey"] == "distance":
                duration += estimate_step_duration(step, sport_type)
            else:
                duration += step["endConditionValue"]
        elif step["type"] == "RepeatGroupDTO":
            child_steps_duration = calculate_steps_duration(step["workoutSteps"], sport_type)
            duration += step["numberOfIterations"] * child_steps_duration

    return duration


def estimate_step_duration(step: dict, sport_type: str) -> int:
    """
    Estimates the duration of a distance-based step.

    Args:
        step: The step to estimate duration for
        sport_type: The sport type key (e.g., 'running')

    Returns:
        The estimated duration in seconds
    """
    distance = step["endConditionValue"]  # distance in meters

    # Check if the step has a pace target
    if (step.get("targetType") and
        step["targetType"]["workoutTargetTypeKey"] == "pace.zone" and
        step.get("targetValueOne") and step.get("targetValueTwo")):
        # Use the average of min and max pace values
        # targetValueOne and targetValueTwo are in m/s, so we convert to seconds per meter
        pace_per_meter = 2 / (step["targetValueOne"] + step["targetValueTwo"])
    elif (step.get("targetType") and
          step["targetType"]["workoutTargetTypeKey"] == "speed.zone" and
          step.get("targetValueOne") and step.get("targetValueTwo")):
        # If speed target, use the average speed in m/s
        avg_speed = (step["targetValueOne"] + step["targetValueTwo"]) / 2
        pace_per_meter = 1 / avg_speed
    else:
        # Use default pace value based on sport type
        pace_per_meter = DEFAULT_PACE.get(sport_type.lower(), DEFAULT_PACE["running"])

    # Calculate estimated duration
    return int(distance * pace_per_meter)