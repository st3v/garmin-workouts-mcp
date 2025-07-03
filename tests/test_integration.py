import pytest
from unittest.mock import patch
from garmin_workouts_mcp.main import mcp, login


class TestMCPIntegration:
    """Integration tests for MCP tool registration and execution."""

    @pytest.mark.asyncio
    async def test_mcp_tools_registered(self):
        """Test that all expected tools are registered with the MCP server."""
        # Get the list of registered tools
        tools = await mcp.get_tools()

        # Expected tool names
        expected_tools = {
            "list_workouts",
            "get_workout",
            "get_calendar",
            "schedule_workout",
            "delete_workout",
            "upload_workout",
            "generate_workout_data_prompt"
        }

        # FastMCP returns tools as a dictionary of FunctionTool objects
        assert isinstance(tools, dict)
        registered_tool_names = set(tools.keys())

        # Assert exact match of tools (no missing, no unexpected)
        missing_tools = expected_tools - registered_tool_names
        unexpected_tools = registered_tool_names - expected_tools

        assert not missing_tools, f"Missing tools: {missing_tools}"
        assert not unexpected_tools, f"Unexpected tools: {unexpected_tools}"
        assert expected_tools == registered_tool_names, f"Tool sets don't match. Expected: {expected_tools}, Found: {registered_tool_names}"

    def test_mcp_server_name(self):
        """Test that the MCP server has the correct name."""
        assert mcp.name == "GarminConnectWorkoutsServer"

    @patch('garmin_workouts_mcp.main.garth.resume')
    @patch('garmin_workouts_mcp.main.garth.save')
    @patch('garmin_workouts_mcp.main.garth.login')
    def test_login_integration_success(self, mock_garth_login, mock_save, mock_resume):
        """Test successful login flow when resume works."""
        # Arrange
        mock_resume.return_value = None

        # Act
        login()

        # Assert
        mock_resume.assert_called_once_with("~/.garth")
        mock_garth_login.assert_not_called()
        mock_save.assert_not_called()

    @patch('garmin_workouts_mcp.main.garth.resume')
    @patch('garmin_workouts_mcp.main.garth.save')
    @patch('garmin_workouts_mcp.main.garth.login')
    @patch.dict('os.environ', {"GARMIN_EMAIL": "test@example.com", "GARMIN_PASSWORD": "password123"})
    def test_login_integration_new_login(self, mock_garth_login, mock_save, mock_resume):
        """Test login flow when resume fails and new login is required via environment variables."""
        # Arrange
        mock_resume.side_effect = Exception("No saved credentials")
        mock_garth_login.return_value = None

        # Act
        login()

        # Assert
        mock_resume.assert_called_once_with("~/.garth")
        mock_garth_login.assert_called_once_with("test@example.com", "password123")
        mock_save.assert_called_once_with("~/.garth")

    @patch('garmin_workouts_mcp.main.garth.resume')
    @patch('garmin_workouts_mcp.main.garth.login')
    @patch.dict('os.environ', {"GARMIN_EMAIL": "test@example.com", "GARMIN_PASSWORD": "password123"})
    @patch('garmin_workouts_mcp.main.sys.exit')
    @patch('garmin_workouts_mcp.main.logger')
    def test_login_integration_login_failure(self, mock_logger, mock_exit, mock_garth_login, mock_resume):
        """Test login flow when garth.login fails."""
        # Arrange
        mock_resume.side_effect = Exception("No saved credentials")
        mock_garth_login.side_effect = Exception("Invalid credentials")

        # Act
        login()

        # Assert
        mock_resume.assert_called_once_with("~/.garth")
        mock_garth_login.assert_called_once_with("test@example.com", "password123")
        mock_logger.error.assert_called_once()
        mock_exit.assert_called_once_with(1)

    @patch('garmin_workouts_mcp.main.garth.resume')
    @patch.dict('os.environ', {}, clear=True)
    def test_login_integration_no_credentials_raises_error(self, mock_resume):
        """Test login flow when no credentials are provided via env vars."""
        # Arrange
        mock_resume.side_effect = Exception("No saved credentials")

        # Act & Assert
        with pytest.raises(ValueError, match=r"Garmin email and password must be provided via environment variables \(GARMIN_EMAIL, GARMIN_PASSWORD\)."):
            login()

        mock_resume.assert_called_once_with("~/.garth")
