
import pytest
from garmin_workouts_mcp.garmin_workout import (
    make_payload,
    get_sport_type,
    process_step,
    process_regular_step,
    process_repeat_step,
    process_target,
    calculate_estimated_duration,
    calculate_value_range,
    calculate_pace_range,
    convert_value_to_unit,
    estimate_step_duration,
    calculate_steps_duration,
    DEFAULT_PACE
)

def test_get_sport_type_unsupported():
    with pytest.raises(ValueError, match="Unsupported sport type: foobar"):
        get_sport_type("foobar")

def test_process_step_missing_type():
    with pytest.raises(ValueError, match="Missing stepType for step: Unnamed Step"):
        process_step({}, 1)

def test_process_regular_step_missing_duration():
    with pytest.raises(ValueError, match="Invalid or missing stepDuration for step: Unnamed Step"):
        process_regular_step({"stepType": "run"}, 1)

def test_process_regular_step_invalid_duration():
    with pytest.raises(ValueError, match="Invalid or missing stepDuration for step: Unnamed Step"):
        process_regular_step({"stepType": "run", "stepDuration": 0}, 1)

def test_process_regular_step_non_numeric_duration():
    with pytest.raises(ValueError, match="Invalid or missing stepDuration for step: Unnamed Step"):
        process_regular_step({"stepType": "run", "stepDuration": "abc"}, 1)

def test_process_repeat_step_missing_iterations():
    with pytest.raises(ValueError, match="Invalid or missing numberOfIterations for repeat step."):
        process_repeat_step({"numberOfIterations": 0, "steps": []}, 1)

def test_process_target_unsupported_type():
    with pytest.raises(ValueError, match="Unsupported target type: heart_rate_zone"):
        process_target({}, {"target": {"type": "heart_rate_zone"}})

def test_make_payload_running_workout_detailed():
    workout_data = {
        "name": "My Detailed Running Workout",
        "type": "running",
        "steps": [
            {"stepType": "warmup", "stepDuration": 600},
            {"stepType": "run", "stepDuration": 1800, "target": {"type": "pace", "value": [6.0, 7.0], "unit": "min_per_km"}},
            {"stepType": "cooldown", "stepDuration": 300}
        ]
    }
    payload = make_payload(workout_data)
    assert payload["workoutName"] == "My Detailed Running Workout"
    assert payload["sportType"]["sportTypeKey"] == "running"
    assert len(payload["workoutSegments"][0]["workoutSteps"]) == 3
    
    warmup_step = payload["workoutSegments"][0]["workoutSteps"][0]
    assert warmup_step["stepType"]["stepTypeKey"] == "warmup"
    assert warmup_step["endCondition"]["conditionTypeKey"] == "time"
    assert warmup_step["endConditionValue"] == 600
    
    run_step = payload["workoutSegments"][0]["workoutSteps"][1]
    assert run_step["stepType"]["stepTypeKey"] == "interval"
    assert run_step["targetType"]["workoutTargetTypeKey"] == "pace.zone"
    assert run_step["endCondition"]["conditionTypeKey"] == "time"
    assert run_step["endConditionValue"] == 1800
    assert run_step["targetValueOne"] == 1000 / (7.0 * 60)
    assert run_step["targetValueTwo"] == 1000 / (6.0 * 60)

def test_make_payload_cycling_workout_detailed():
    workout_data = {
        "name": "My Detailed Cycling Workout",
        "type": "cycling",
        "steps": [
            {"stepType": "warmup", "stepDuration": 900},
            {"stepType": "bike", "stepDuration": 3600, "target": {"type": "power", "value": [150, 200]}},
            {"stepType": "cooldown", "stepDuration": 600}
        ]
    }
    payload = make_payload(workout_data)
    assert payload["workoutName"] == "My Detailed Cycling Workout"
    assert payload["sportType"]["sportTypeKey"] == "cycling"
    assert len(payload["workoutSegments"][0]["workoutSteps"]) == 3

    bike_step = payload["workoutSegments"][0]["workoutSteps"][1]
    assert bike_step["stepType"]["stepTypeKey"] == "interval"
    assert bike_step["targetType"]["workoutTargetTypeKey"] == "power.zone"
    assert bike_step["targetValueOne"] == 150
    assert bike_step["targetValueTwo"] == 200

def test_calculate_estimated_duration_with_repeat():
    workout_segments = [
        {
            "sportType": {"sportTypeKey": "running"},
            "workoutSteps": [
                {"type": "ExecutableStepDTO", "endCondition": {"conditionTypeKey": "time"}, "endConditionValue": 600},
                {
                    "type": "RepeatGroupDTO",
                    "numberOfIterations": 2,
                    "workoutSteps": [
                        {"type": "ExecutableStepDTO", "endCondition": {"conditionTypeKey": "time"}, "endConditionValue": 300},
                        {"type": "ExecutableStepDTO", "endCondition": {"conditionTypeKey": "distance"}, "endConditionValue": 1000, "targetType": {"workoutTargetTypeKey": "pace.zone"}, "targetValueOne": 2.77, "targetValueTwo": 3.33}
                    ]
                }
            ]
        }
    ]
    duration = calculate_estimated_duration(workout_segments)
    assert duration == 600 + 2 * (300 + int(1000 * (2 / (2.77 + 3.33))))

def test_process_regular_step_distance_meters():
    step_data = {
        "stepType": "run",
        "endConditionType": "distance",
        "stepDistance": 1000,
        "distanceUnit": "m"
    }
    result = process_regular_step(step_data, 1)
    assert result["step"]["endCondition"]["conditionTypeKey"] == "distance"
    assert result["step"]["endConditionValue"] == 1000

def test_process_regular_step_distance_kilometers():
    step_data = {
        "stepType": "run",
        "endConditionType": "distance",
        "stepDistance": 5,
        "distanceUnit": "km"
    }
    result = process_regular_step(step_data, 1)
    assert result["step"]["endCondition"]["conditionTypeKey"] == "distance"
    assert result["step"]["endConditionValue"] == 5000

def test_process_regular_step_distance_kilometers_round():
    step_data = {
        "stepType": "run",
        "endConditionType": "distance",
        "stepDistance": 1.000,
        "distanceUnit": "km"
    }
    result = process_regular_step(step_data, 1)
    assert result["step"]["endCondition"]["conditionTypeKey"] == "distance"
    assert result["step"]["endConditionValue"] == 1000 # Should be rounded to 1000

def test_process_regular_step_distance_miles():
    step_data = {
        "stepType": "run",
        "endConditionType": "distance",
        "stepDistance": 2,
        "distanceUnit": "mile"
    }
    result = process_regular_step(step_data, 1)
    assert result["step"]["endCondition"]["conditionTypeKey"] == "distance"
    assert result["step"]["endConditionValue"] == 2 * 1609.344

def test_process_regular_step_unsupported_distance_unit():
    step_data = {
        "stepType": "run",
        "endConditionType": "distance",
        "stepDistance": 10,
        "distanceUnit": "yard"
    }
    with pytest.raises(ValueError, match="Unsupported distance unit: yard"):
        process_regular_step(step_data, 1)

def test_process_target_speed():
    workout_step = {}
    step_data = {"target": {"type": "speed", "value": [3.0, 4.0]}}
    process_target(workout_step, step_data)
    assert workout_step["targetType"]["workoutTargetTypeKey"] == "speed.zone"
    assert workout_step["targetValueOne"] == 3.0
    assert workout_step["targetValueTwo"] == 4.0

def test_process_target_heart_rate():
    workout_step = {}
    step_data = {"target": {"type": "heart rate", "value": [120, 150]}}
    process_target(workout_step, step_data)
    assert workout_step["targetType"]["workoutTargetTypeKey"] == "heart.rate.zone"
    assert workout_step["targetValueOne"] == 120
    assert workout_step["targetValueTwo"] == 150

def test_process_target_cadence():
    workout_step = {}
    step_data = {"target": {"type": "cadence", "value": [80, 90]}}
    process_target(workout_step, step_data)
    assert workout_step["targetType"]["workoutTargetTypeKey"] == "cadence.zone"
    assert workout_step["targetValueOne"] == 80
    assert workout_step["targetValueTwo"] == 90

def test_process_target_power():
    workout_step = {}
    step_data = {"target": {"type": "power", "value": [200, 250]}}
    process_target(workout_step, step_data)
    assert workout_step["targetType"]["workoutTargetTypeKey"] == "power.zone"
    assert workout_step["targetValueOne"] == 200
    assert workout_step["targetValueTwo"] == 250

def test_calculate_value_range_default():
    min_val, max_val = calculate_value_range(100, "some_other_target")
    assert min_val == 95.0
    assert max_val == 105.0

def test_calculate_pace_range():
    min_pace, max_pace = calculate_pace_range(6.0)
    assert min_pace == pytest.approx(6.0 - (10/60))
    assert max_pace == pytest.approx(6.0 + (10/60))

def test_convert_value_to_unit_min_per_km():
    converted_value = convert_value_to_unit(6.0, "min_per_km")
    assert converted_value == pytest.approx(1000 / (6.0 * 60))

def test_convert_value_to_unit_other():
    converted_value = convert_value_to_unit(100, "bpm")
    assert converted_value == 100

def test_estimate_step_duration_pace_target():
    step = {
        "endConditionValue": 1000, # meters
        "targetType": {"workoutTargetTypeKey": "pace.zone"},
        "targetValueOne": 2.77, # m/s (slower)
        "targetValueTwo": 3.33  # m/s (faster)
    }
    duration = estimate_step_duration(step, "running")
    assert duration == int(1000 * (2 / (2.77 + 3.33)))

def test_estimate_step_duration_speed_target():
    step = {
        "endConditionValue": 1000, # meters
        "targetType": {"workoutTargetTypeKey": "speed.zone"},
        "targetValueOne": 2.0, # m/s
        "targetValueTwo": 3.0  # m/s
    }
    duration = estimate_step_duration(step, "running")
    assert duration == int(1000 * (1 / ((2.0 + 3.0) / 2)))

def test_estimate_step_duration_default_pace():
    step = {
        "endConditionValue": 1000, # meters
    }
    duration = estimate_step_duration(step, "running")
    assert duration == int(1000 * DEFAULT_PACE["running"])

def test_calculate_steps_duration_mixed_steps():
    steps = [
        {"type": "ExecutableStepDTO", "endCondition": {"conditionTypeKey": "time"}, "endConditionValue": 300},
        {"type": "ExecutableStepDTO", "endCondition": {"conditionTypeKey": "distance"}, "endConditionValue": 500, "targetType": {"workoutTargetTypeKey": "pace.zone"}, "targetValueOne": 2.77, "targetValueTwo": 3.33},
        {
            "type": "RepeatGroupDTO",
            "numberOfIterations": 2,
            "workoutSteps": [
                {"type": "ExecutableStepDTO", "endCondition": {"conditionTypeKey": "time"}, "endConditionValue": 60},
                {"type": "ExecutableStepDTO", "endCondition": {"conditionTypeKey": "distance"}, "endConditionValue": 100, "targetType": {"workoutTargetTypeKey": "pace.zone"}, "targetValueOne": 2.77, "targetValueTwo": 3.33}
            ]
        }
    ]
    duration = calculate_steps_duration(steps, "running")
    expected_duration = 300 + int(500 * (2 / (2.77 + 3.33))) + 2 * (60 + int(100 * (2 / (2.77 + 3.33))))
    assert duration == expected_duration
