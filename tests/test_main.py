import pytest
from unittest.mock import patch


class TestListWorkouts:
    """Test cases for the list_workouts tool."""

    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_list_workouts_success(self, mock_connectapi):
        """Test successful retrieval of workouts."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        list_workouts_func = main_module.list_workouts.fn

        # Arrange
        expected_workouts = [
            {
                "workoutId": "12345",
                "workoutName": "Easy Run",
                "sportType": {"sportTypeKey": "running"},
                "estimatedDurationInSecs": 1800
            },
            {
                "workoutId": "67890",
                "workoutName": "Bike Intervals",
                "sportType": {"sportTypeKey": "cycling"},
                "estimatedDurationInSecs": 3600
            }
        ]
        mock_connectapi.return_value = expected_workouts

        # Act
        result = list_workouts_func()

        # Assert
        mock_connectapi.assert_called_once_with("/workout-service/workouts")
        assert result == {"workouts": expected_workouts}
        assert len(result["workouts"]) == 2
        assert result["workouts"][0]["workoutName"] == "Easy Run"
        assert result["workouts"][1]["workoutName"] == "Bike Intervals"

    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_list_workouts_empty_list(self, mock_connectapi):
        """Test when no workouts are returned."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        list_workouts_func = main_module.list_workouts.fn

        # Arrange
        mock_connectapi.return_value = []

        # Act
        result = list_workouts_func()

        # Assert
        mock_connectapi.assert_called_once_with("/workout-service/workouts")
        assert result == {"workouts": []}
        assert len(result["workouts"]) == 0

    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_list_workouts_api_error(self, mock_connectapi):
        """Test when the Garmin API raises an exception."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        list_workouts_func = main_module.list_workouts.fn

        # Arrange
        mock_connectapi.side_effect = Exception("API connection failed")

        # Act & Assert
        with pytest.raises(Exception, match="API connection failed"):
            list_workouts_func()

        mock_connectapi.assert_called_once_with("/workout-service/workouts")

    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_list_workouts_none_response(self, mock_connectapi):
        """Test when the API returns None."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        list_workouts_func = main_module.list_workouts.fn

        # Arrange
        mock_connectapi.return_value = None

        # Act
        result = list_workouts_func()

        # Assert
        mock_connectapi.assert_called_once_with("/workout-service/workouts")
        assert result == {"workouts": None}


class TestGetWorkout:
    """Test cases for the get_workout tool."""

    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_get_workout_success(self, mock_connectapi):
        """Test successful retrieval of a specific workout."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        get_workout_func = main_module.get_workout.fn

        # Arrange
        workout_id = "12345"
        expected_workout = {
            "workoutId": workout_id,
            "workoutName": "Test Workout",
            "sportType": {"sportTypeKey": "running"}
        }
        mock_connectapi.return_value = expected_workout

        # Act
        result = get_workout_func(workout_id)

        # Assert
        mock_connectapi.assert_called_once_with(f"/workout-service/workout/{workout_id}")
        assert result == {"workout": expected_workout}
        assert result["workout"]["workoutId"] == workout_id

    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_get_workout_not_found(self, mock_connectapi):
        """Test get_workout when the workout is not found."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        get_workout_func = main_module.get_workout.fn

        # Arrange
        workout_id = "non_existent_id"
        mock_connectapi.return_value = None

        # Act
        result = get_workout_func(workout_id)

        # Assert
        mock_connectapi.assert_called_once_with(f"/workout-service/workout/{workout_id}")
        assert result == {"workout": None}

    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_get_workout_api_error(self, mock_connectapi):
        """Test get_workout when the API call fails."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        get_workout_func = main_module.get_workout.fn

        # Arrange
        workout_id = "12345"
        mock_connectapi.side_effect = Exception("API Error")

        # Act & Assert
        with pytest.raises(Exception, match="API Error"):
            get_workout_func(workout_id)


class TestScheduleWorkout:
    """Test cases for the schedule_workout tool."""

    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_schedule_workout_success(self, mock_connectapi):
        """Test successful workout scheduling."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        schedule_workout_func = main_module.schedule_workout.fn

        # Arrange
        workout_id = "12345"
        date = "2024-01-15"
        expected_response = {"workoutScheduleId": "schedule_456"}
        mock_connectapi.return_value = expected_response

        # Act
        result = schedule_workout_func(workout_id, date)

        # Assert
        mock_connectapi.assert_called_once_with(
            f"/workout-service/schedule/{workout_id}",
            method="POST",
            json={"date": date}
        )
        assert result == {"workoutScheduleId": "schedule_456"}

    def test_schedule_workout_invalid_date_format(self,):
        """Test schedule_workout with invalid date format."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        schedule_workout_func = main_module.schedule_workout.fn

        with pytest.raises(ValueError, match=r"Date must be in ISO format \(YYYY-MM-DD\)"):
            schedule_workout_func("123", "01/15/2024")

    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_schedule_workout_api_error(self, mock_connectapi):
        """Test schedule_workout when the API call fails."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        schedule_workout_func = main_module.schedule_workout.fn

        # Arrange
        workout_id = "12345"
        date = "2024-01-15"
        mock_connectapi.side_effect = Exception("API Error")

        # Act & Assert
        with pytest.raises(Exception, match="API Error"):
            schedule_workout_func(workout_id, date)




class TestDeleteWorkout:
    """Test cases for the delete_workout tool."""

    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_delete_workout_success(self, mock_connectapi):
        """Test successful workout deletion."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        delete_workout_func = main_module.delete_workout.fn

        # Arrange
        workout_id = "12345"
        mock_connectapi.return_value = None

        # Act
        result = delete_workout_func(workout_id)

        # Assert
        mock_connectapi.assert_called_once_with(
            f"/workout-service/workout/{workout_id}",
            method="DELETE"
        )
        assert result is True

    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_delete_workout_api_error(self, mock_connectapi):
        """Test delete_workout when API raises an exception."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        delete_workout_func = main_module.delete_workout.fn

        # Arrange
        workout_id = "12345"
        mock_connectapi.side_effect = Exception("API error")

        # Act
        result = delete_workout_func(workout_id)

        # Assert
        mock_connectapi.assert_called_once_with(
            f"/workout-service/workout/{workout_id}",
            method="DELETE"
        )
        assert result is False


class TestGenerateWorkoutDataPrompt:
    """Test cases for the generate_workout_data_prompt tool."""

    def test_generate_workout_data_prompt_success(self):
        """Test successful prompt generation."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        generate_workout_data_prompt_func = main_module.generate_workout_data_prompt.fn

        # Arrange
        description = "30 minute easy run"

        # Act
        result = generate_workout_data_prompt_func(description)

        # Assert
        assert "prompt" in result
        assert description in result["prompt"]
        assert "JSON" in result["prompt"]
        assert "upload_workout" in result["prompt"]
        assert "min/km" in result["prompt"]


class TestUploadWorkout:
    """Test cases for the upload_workout tool."""

    @patch('garmin_workouts_mcp.main.make_payload')
    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_upload_workout_success(self, mock_connectapi, mock_make_payload):
        """Test successful workout upload."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        upload_workout_func = main_module.upload_workout.fn

        # Arrange
        workout_data = {
            "name": "Test Workout",
            "type": "running",
            "steps": []
        }
        mock_payload = {"workoutName": "Test Workout"}
        mock_make_payload.return_value = mock_payload
        mock_connectapi.return_value = {"workoutId": "new_workout_123"}

        # Act
        result = upload_workout_func(workout_data)

        # Assert
        assert result["workoutId"] == "new_workout_123"
        mock_make_payload.assert_called_once_with(workout_data)
        mock_connectapi.assert_called_once_with(
            "/workout-service/workout",
            method="POST",
            json=mock_payload
        )

    @patch('garmin_workouts_mcp.main.make_payload')
    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_upload_workout_no_workout_id(self, mock_connectapi, mock_make_payload):
        """Test upload_workout when no workout ID is returned."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        upload_workout_func = main_module.upload_workout.fn

        # Arrange
        workout_data = {"name": "Test Workout", "type": "running", "steps": []}
        mock_make_payload.return_value = {}
        mock_connectapi.return_value = {}  # No workoutId

        # Act & Assert
        with pytest.raises(Exception, match="No workout ID returned"):
            upload_workout_func(workout_data)

class TestGetCalendar:
    """Test cases for the get_calendar tool."""

    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_get_calendar_monthly_success(self, mock_connectapi):
        """Test successful retrieval of monthly calendar data."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        get_calendar_func = main_module.get_calendar.fn

        # Arrange
        year, month = 2025, 6
        expected_calendar = {
            "calendarItems": [
                {
                    "date": "2025-06-01",
                    "workouts": [],
                    "activities": []
                }
            ]
        }
        mock_connectapi.return_value = expected_calendar

        # Act
        result = get_calendar_func(year, month)

        # Assert
        mock_connectapi.assert_called_once_with("/calendar-service/year/2025/month/5")
        assert result["calendar"] == expected_calendar
        assert result["view_type"] == "month"
        assert result["period"]["year"] == year
        assert result["period"]["month"] == month
        assert result["period"]["day"] is None
        assert result["period"]["start"] is None

    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_get_calendar_weekly_success(self, mock_connectapi):
        """Test successful retrieval of weekly calendar data."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        get_calendar_func = main_module.get_calendar.fn

        # Arrange
        year, month, day = 2025, 6, 10
        expected_calendar = {
            "calendarItems": [
                {
                    "date": "2025-06-10",
                    "workouts": [{"workoutId": "123", "workoutName": "Morning Run"}],
                    "activities": []
                }
            ]
        }
        mock_connectapi.return_value = expected_calendar

        # Act
        result = get_calendar_func(year, month, day)

        # Assert
        mock_connectapi.assert_called_once_with("/calendar-service/year/2025/month/5/day/10/start/1")
        assert result["calendar"] == expected_calendar
        assert result["view_type"] == "week"
        assert result["period"]["year"] == year
        assert result["period"]["month"] == month
        assert result["period"]["day"] == day
        assert result["period"]["start"] == 1

    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_get_calendar_weekly_custom_start(self, mock_connectapi):
        """Test weekly calendar with custom start parameter."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        get_calendar_func = main_module.get_calendar.fn

        # Arrange
        year, month, day, start = 2025, 6, 10, 2
        mock_connectapi.return_value = {}

        # Act
        result = get_calendar_func(year, month, day, start)

        # Assert
        mock_connectapi.assert_called_once_with("/calendar-service/year/2025/month/5/day/10/start/2")
        assert result["view_type"] == "week"
        assert result["period"]["start"] == 2

    def test_get_calendar_invalid_year(self):
        """Test get_calendar with invalid year."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        get_calendar_func = main_module.get_calendar.fn

        # Test year too low
        with pytest.raises(ValueError, match="Year must be between 1900 and 2100, got 1899"):
            get_calendar_func(1899, 6)

        # Test year too high
        with pytest.raises(ValueError, match="Year must be between 1900 and 2100, got 2101"):
            get_calendar_func(2101, 6)

    def test_get_calendar_invalid_month(self):
        """Test get_calendar with invalid month."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        get_calendar_func = main_module.get_calendar.fn

        # Test month too low
        with pytest.raises(ValueError, match="Month must be between 1 and 12, got 0"):
            get_calendar_func(2025, 0)

        # Test month too high
        with pytest.raises(ValueError, match="Month must be between 1 and 12, got 13"):
            get_calendar_func(2025, 13)

    def test_get_calendar_invalid_day(self):
        """Test get_calendar with invalid day."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        get_calendar_func = main_module.get_calendar.fn

        # Test day too low
        with pytest.raises(ValueError, match="Day must be between 1 and 31, got 0"):
            get_calendar_func(2025, 6, 0)

        # Test day too high
        with pytest.raises(ValueError, match="Day must be between 1 and 31, got 32"):
            get_calendar_func(2025, 6, 32)

    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_get_calendar_empty_response(self, mock_connectapi):
        """Test get_calendar when API returns empty response."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        get_calendar_func = main_module.get_calendar.fn

        # Arrange
        mock_connectapi.return_value = None

        # Act
        result = get_calendar_func(2025, 6)

        # Assert
        assert result["calendar"] is None
        assert result["view_type"] == "month"

    @patch('garmin_workouts_mcp.main.garth.connectapi')
    def test_get_calendar_api_error(self, mock_connectapi):
        """Test get_calendar when API raises an exception."""
        # Import the actual function, not the FunctionTool wrapper
        import garmin_workouts_mcp.main as main_module
        get_calendar_func = main_module.get_calendar.fn

        # Arrange
        mock_connectapi.side_effect = Exception("API connection failed")

        # Act & Assert
        with pytest.raises(Exception, match="API connection failed"):
            get_calendar_func(2025, 6)

        mock_connectapi.assert_called_once_with("/calendar-service/year/2025/month/5")
