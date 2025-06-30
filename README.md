# Garmin Workouts MCP Server

An MCP server that allows you to create, list, and manage Garmin Connect workouts using natural language descriptions through MCP-compatible clients.

## Features

- **Create workouts**: Generate structured Garmin workouts from natural language descriptions using AI
- **List workouts**: View all your existing workouts on Garmin Connect
- **Get workout details**: Retrieve detailed information about specific workouts
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
      "args": ["garmin-workouts-mcp"]
    }
  }
}
```

On first use, you'll be prompted to login to Garmin Connect. Upon successful login, access and refresh tokens will be stored locally for subsequent calls.

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

- `GARTH_HOME`: Custom location for Garmin credentials (optional, defaults to `~/.garth`)
