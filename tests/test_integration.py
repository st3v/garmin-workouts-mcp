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
            "schedule_workout",
            "delete_workout",
            "upload_workout",
            "generate_workout_data_prompt"
        }

        # FastMCP returns tools as a dictionary of FunctionTool objects
        assert isinstance(tools, dict)
        registered_tool_names = set(tools.keys())

        # Assert all expected tools are registered
        assert expected_tools.issubset(registered_tool_names), f"Missing tools: {expected_tools - registered_tool_names}"

    def test_mcp_server_name(self):
        """Test that the MCP server has the correct name."""
        assert mcp.name == "GarminConnectWorkoutsServer"

    @patch('garmin_workouts_mcp.main.garth.resume')
    @patch('garmin_workouts_mcp.main.garth.save')
    @patch('garmin_workouts_mcp.main.garth.login')
    @patch('builtins.input')
    @patch('garmin_workouts_mcp.main.getpass')
    def test_login_integration_success(self, mock_getpass, mock_input, mock_garth_login, mock_save, mock_resume):
        """Test successful login flow when resume works."""
        # Arrange
        mock_resume.return_value = None

        # Act
        login()

        # Assert
        mock_resume.assert_called_once_with("~/.garth")
        mock_input.assert_not_called()
        mock_getpass.assert_not_called()
        mock_garth_login.assert_not_called()
        mock_save.assert_not_called()

    @patch('garmin_workouts_mcp.main.garth.resume')
    @patch('garmin_workouts_mcp.main.garth.save')
    @patch('garmin_workouts_mcp.main.garth.login')
    @patch('builtins.input')
    @patch('garmin_workouts_mcp.main.getpass')
    def test_login_integration_new_login(self, mock_getpass, mock_input, mock_garth_login, mock_save, mock_resume):
        """Test login flow when resume fails and new login is required."""
        # Arrange
        mock_resume.side_effect = Exception("No saved credentials")
        mock_input.return_value = "test@example.com"
        mock_getpass.return_value = "password123"
        mock_garth_login.return_value = None

        # Act
        login()

        # Assert
        mock_resume.assert_called_once_with("~/.garth")
        mock_input.assert_called_once_with("Enter email address: ")
        mock_getpass.assert_called_once_with("Enter password: ")
        mock_garth_login.assert_called_once_with("test@example.com", "password123")
        mock_save.assert_called_once_with("~/.garth")

    @patch('garmin_workouts_mcp.main.garth.resume')
    @patch('garmin_workouts_mcp.main.garth.login')
    @patch('builtins.input')
    @patch('garmin_workouts_mcp.main.getpass')
    @patch('garmin_workouts_mcp.main.sys.exit')
    @patch('garmin_workouts_mcp.main.logger')
    def test_login_integration_login_failure(self, mock_logger, mock_exit, mock_getpass, mock_input, mock_garth_login, mock_resume):
        """Test login flow when garth.login fails."""
        # Arrange
        mock_resume.side_effect = Exception("No saved credentials")
        mock_input.return_value = "test@example.com"
        mock_getpass.return_value = "password123"
        mock_garth_login.side_effect = Exception("Invalid credentials")

        # Act
        login()

        # Assert
        mock_resume.assert_called_once_with("~/.garth")
        mock_input.assert_called_once_with("Enter email address: ")
        mock_getpass.assert_called_once_with("Enter password: ")
        mock_garth_login.assert_called_once_with("test@example.com", "password123")
        mock_logger.error.assert_called_once()
        mock_exit.assert_called_once_with(1)
