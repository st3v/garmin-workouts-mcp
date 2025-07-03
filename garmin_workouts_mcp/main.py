from fastmcp import FastMCP
import garth
import os
import sys
import logging
from datetime import datetime
from .garmin_workout import make_payload

LIST_WORKOUTS_ENDPOINT = "/workout-service/workouts"
GET_WORKOUT_ENDPOINT = "/workout-service/workout/{workout_id}"
CREATE_WORKOUT_ENDPOINT = "/workout-service/workout"
SCHEDULE_WORKOUT_ENDPOINT = "/workout-service/schedule/{workout_id}"
CALENDAR_WEEK_ENDPOINT = "/calendar-service/year/{year}/month/{month}/day/{day}/start/{start}"
CALENDAR_MONTH_ENDPOINT = "/calendar-service/year/{year}/month/{month}"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

mcp = FastMCP(name="GarminConnectWorkoutsServer")

@mcp.tool
def list_workouts() -> dict:
    """
    List all workouts available on Garmin Connect.

    Returns:
        A dictionary containing a list of workouts.
    """
    workouts = garth.connectapi(LIST_WORKOUTS_ENDPOINT)
    return {"workouts": workouts}

@mcp.tool
def get_workout(workout_id: str) -> dict:
    """
    Get details of a specific workout by its ID.

    Args:
        workout_id: ID of the workout to retrieve.

    Returns:
        Workout details as a dictionary.
    """
    endpoint = GET_WORKOUT_ENDPOINT.format(workout_id=workout_id)
    workout = garth.connectapi(endpoint)
    return {"workout": workout}

@mcp.tool
def schedule_workout(workout_id: str, date: str) -> dict:
    """
    Schedule a workout on Garmin Connect.

    Args:
        workout_id: ID of the workout to schedule.
        date: Date to schedule the workout in ISO format (YYYY-MM-DD).

    Returns:
        workoutScheduleId: ID of the scheduled workout.

    Raises:
        ValueError: If the date format is incorrect.
        Exception: If scheduling the workout fails.
    """

    # verify date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Date must be in ISO format (YYYY-MM-DD)")

    payload = {
        "date": date,
    }

    endpoint = SCHEDULE_WORKOUT_ENDPOINT.format(workout_id=workout_id)
    result = garth.connectapi(endpoint, method="POST", json=payload)
    workout_scheduled_id = result.get("workoutScheduleId")
    if workout_scheduled_id is None:
        raise Exception(f"Scheduling workout failed: {result}")

    return {"workoutScheduleId": str(workout_scheduled_id)}

@mcp.tool
def delete_workout(workout_id: str) -> bool:
    """
    Delete a workout from Garmin Connect.

    Args:
        workout_id: ID of the workout to delete.

    Returns:
        True if the deletion was successful, False otherwise.
    """
    endpoint = GET_WORKOUT_ENDPOINT.format(workout_id=workout_id)

    try:
        garth.connectapi(endpoint, method="DELETE")
        logger.info("Workout %s deleted successfully", workout_id)
        return True
    except Exception as e:
        logger.error("Failed to delete workout %s: %s", workout_id, e)
        return False

@mcp.tool
def upload_workout(workout_data: dict) -> dict:
    """
    Uploads a structured workout to Garmin Connect.

    Args:
        workout_data: Workout data in JSON format to upload. Use the `generate_workout_data_prompt` tool to create a prompt for the LLM to generate this data.

    Returns:
        The uploaded workout's ID on Garmin Connect.

    Raises:
        Exception: If the upload fails or the workout ID is not returned.
    """

    logger.info("Workout data received from client: %s", workout_data)

    try:
        # Convert to Garmin payload format
        payload = make_payload(workout_data)

        # logging the payload for debugging
        logger.info("Payload to be sent to Garmin Connect: %s", payload)

        # Create workout on Garmin Connect
        result = garth.connectapi("/workout-service/workout", method="POST", json=payload)

        # logging the result for debugging
        logger.info("Response from Garmin Connect: %s", result)

        workout_id = result.get("workoutId")

        if workout_id is None:
            raise Exception("No workout ID returned")

        return {"workoutId": str(workout_id)}

    except Exception as e:
        raise Exception(f"Failed to upload workout to Garmin Connect: {str(e)}")

@mcp.tool
def get_calendar(year: int, month: int, day: int = None, start: int = 1) -> dict:
    """
    Get calendar data from Garmin Connect for different time periods.

    Args:
        year: Year (e.g., 2025)
        month: Month (1-12)
        day: Day of month (1-31). If provided, gets corresponding weekly view that includes this day.
             If omitted, gets monthly view for the entire month.
        start: Day offset for weekly queries (defaults to 1). Controls which day of the week
               the 7-day period begins. Each increment shifts the start date forward by one day:
               - start=0: Week starts on Sunday
               - start=1: Week starts on Monday (DEFAULT)
               - start=2: Week starts on Tuesday
               - start=3: Week starts on Wednesday
               - start=4: Week starts on Thursday
               And so on. Different start values return different 7-day windows with varying
               calendar items, useful for different training schedules and calendar preferences.

    Returns:
        Calendar data with workouts and activities for the specified period.

    Raises:
        ValueError: If any of the date parameters are invalid.
    """
    # Input validation
    if not (1900 <= year <= 2100):
        raise ValueError(f"Year must be between 1900 and 2100, got {year}")

    if not (1 <= month <= 12):
        raise ValueError(f"Month must be between 1 and 12, got {month}")

    if day is not None:
        if not (1 <= day <= 31):
            raise ValueError(f"Day must be between 1 and 31, got {day}")

    # Convert month from 1-based (human readable) to 0-based (Garmin API)
    garmin_month = month - 1

    if day is not None:
        # Weekly view
        endpoint = CALENDAR_WEEK_ENDPOINT.format(
            year=year, month=garmin_month, day=day, start=start
        )
        view_type = "week"
    else:
        # Monthly view (default)
        endpoint = CALENDAR_MONTH_ENDPOINT.format(
            year=year, month=garmin_month
        )
        view_type = "month"

    calendar_data = garth.connectapi(endpoint)

    return {
        "calendar": calendar_data,
        "view_type": view_type,
        "period": {
            "year": year,
            "month": month,
            "day": day,
            "start": start if day else None
        }
    }

@mcp.tool
def generate_workout_data_prompt(description: str) -> dict:
    """
    Generate prompt for LLM to create structured workout data based on a natural language description. The LLM
    should use the returned prompt to generate a JSON object that can then be used with the `upload_workout` tool.

    Args:
        description: Natural language description of the workout

    Returns:
        Prompt for the LLM to generate structured workout data
    """

    return {"prompt": f"""
    You are a fitness coach.
    Given the following workout description, create a structured JSON object that represents the workout.
    The generated JSON should be compatible with the `upload_workout` tool.

    Workout Description:
    {description}

    Requirements:
    - The output must be valid JSON.
    - For pace targets, use decimal minutes per km (e.g., 4:40 min/km = 4.67 minutes per km)
    - For time-based steps, use stepDuration in seconds
    - For distance-based steps, use stepDistance with appropriate distanceUnit
    - Use the following structure for the workout object:
    {{
    "name": "Workout Name",
    "type": "running" | "cycling" | "swimming" | "walking" | "cardio" | "strength",
    "steps": [
        {{
        "stepName": "Step Name",
        "stepDescription": "Description",
        "endConditionType": "time" | "distance",
        "stepDuration": duration_in_seconds,
        "stepDistance": distance_value,
        "distanceUnit": "m" | "km" | "mile",
        "stepType": "warmup" | "cooldown" | "interval" | "recovery" | "rest" | "repeat",
        "target": {{
            "type": "no target" | "pace" | "heart rate" | "power" | "cadence" | "speed",
            "value": [minValue, maxValue] | singleValue,
            "unit": "min_per_km" | "bpm" | "watts"
        }},
        "numberOfIterations": number,
        "steps": []
        }}
    ]
    }}

    Examples:
    - For 4:40 min/km pace: "value": 4.67 or "value": [4.5, 4.8]
    - For 160 bpm heart rate: "value": 160 or "value": [150, 170]
    - For no target: "type": "no target", "value": null, "unit": null
    """}

def login():
    """Login to Garmin Connect."""
    garth_home = os.environ.get("GARTH_HOME", "~/.garth")
    try:
        garth.resume(garth_home)
    except Exception:
        email = os.environ.get("GARMIN_EMAIL")
        password = os.environ.get("GARMIN_PASSWORD")

        if not email or not password:
            raise ValueError("Garmin email and password must be provided via environment variables (GARMIN_EMAIL, GARMIN_PASSWORD).")

        try:
            garth.login(email, password)
        except Exception as e:
            logger.error("Login failed: %s", e)
            sys.exit(1)

        # Save credentials for future use
        garth.save(garth_home)

def main():
    """Main entry point for the console script."""
    login()
    mcp.run()

if __name__ == "__main__":
    main()
