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
