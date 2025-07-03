# Garmin Workouts MCP Server

An MCP server that allows you to create, list, and manage Garmin Connect workouts using natural language descriptions through MCP-compatible clients.

## Features

- **Create workouts**: Generate structured Garmin workouts from natural language descriptions using AI
- **List workouts**: View all your existing workouts on Garmin Connect
- **Get workout details**: Retrieve detailed information about specific workouts
- **Schedule workouts**: Schedule workouts on specific dates in Garmin Connect
- **Delete workouts**: Remove workouts from Garmin Connect
- **MCP Integration**: Works with any MCP-compatible client (Claude Desktop, etc.)

## Setup

1. Install and run using uvx:
```bash
uvx garmin-workouts-mcp
```

2. Configure in your MCP client (e.g., Claude Desktop):

Add to your MCP client configuration:
```json
{
  "mcpServers": {
    "garmin-workouts": {
      "command": "uvx",
      "args": ["garmin-workouts-mcp"],
      "env": { # See Authentication section for details
        "GARMIN_EMAIL": "your_email@example.com",
        "GARMIN_PASSWORD": "your_password"
      }
    }
  }
}
```

## Authentication

The Garmin Workouts MCP Server authenticates with Garmin Connect using `garth` [[https://github.com/matin/garth](https://github.com/matin/garth)]. There are two primary ways to provide your Garmin credentials:

### 1. Using Environment Variables

You can set your Garmin Connect email and password as environment variables before starting the MCP server.

- `GARMIN_EMAIL`: Your Garmin Connect email address.
- `GARMIN_PASSWORD`: Your Garmin Connect password.

Example:
```bash
export GARMIN_EMAIL="your_email@example.com"
export GARMIN_PASSWORD="your_password"
uvx garmin-workouts-mcp
```

### 2. Out-of-Band Authentication with `garth`

Alternatively, you can log in to Garmin Connect once using the `garth` library directly and save your authentication tokens to a directory, which the MCP server will then use for subsequent sessions. This method is useful if you prefer not to store your credentials as environment variables or as part of your MCP client configuration.

To log in out-of-band:

1.  Install `garth`:
    ```bash
    pip install garth
    ```
2.  Run the following Python script in your terminal:
    ```python
    import garth
    from getpass import getpass

    email = input("Enter email address: ")
    password = getpass("Enter password: ")
    # If there's MFA, you'll be prompted during the login
    garth.login(email, password)

    garth.save("~/.garth")
    ```
    Follow the prompts to enter your Garmin Connect email and password. Upon successful login, `garth` will save your authentication tokens to `~/.garth`.

    The MCP server will automatically look for these saved tokens. If you wish to store them in a custom location, you can set the `GARTH_HOME` environment variable.

## Usage

This server provides the following MCP tools that can be used through any MCP-compatible client:

### Generate Workout Data Prompt

Use the `generate_workout_data_prompt` tool to create a prompt for an LLM to generate structured workout data:

```
generate_workout_data_prompt("10 min warmup, 5x(1km at 4:30 pace, 2min recovery), 10 min cooldown")
```

### Upload Workout

Use the `upload_workout` tool to upload structured workout data to Garmin Connect:

```
upload_workout(workout_data_json)
```

### Schedule Workout

Use the `schedule_workout` tool to schedule a workout on a specific date:

```
schedule_workout("workout_id_here", "2024-01-15")
```

### Delete Workout

Use the `delete_workout` tool to remove a workout from Garmin Connect:

```
delete_workout("workout_id_here")
```

### List Workouts

```
list_workouts()
```

### Get Workout Details

```
get_workout("workout_id_here")
```

The tool supports various workout types:
- **Running**: pace targets, distance/time based intervals
- **Cycling**: power, cadence, speed targets
- **Swimming**: time/distance based sets
- **Strength training**: circuit-style workouts
- **General cardio**: heart rate based training

## Workout Description Examples

- `"30min easy run at conversational pace"`
- `"5km tempo run at 4:15 min/km pace"`
- `"10 min warmup, 3x(20min at 280w, 5min at 150w), 10min cooldown"`
- `"Swimming: 400m warmup, 8x(50m sprint, 30s rest), 400m cooldown"`
- `"Strength circuit: 5x(30s pushups, 30s squats, 30s plank, 60s rest)"`

## Environment Variables

- `GARMIN_EMAIL`: Your Garmin Connect email address (optional)
- `GARMIN_PASSWORD`: Your Garmin Connect password (optional)
- `GARTH_HOME`: Custom location for Garmin credentials (optional, defaults to `~/.garth`)


## Credits

This project incorporates ideas and prompt designs inspired by [openai-garmin-workout](https://github.com/veelenga/openai-garmin-workout), which is licensed under the MIT License.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
