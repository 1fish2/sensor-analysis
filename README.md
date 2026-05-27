# 📊 CO2 Sensor Comparison Script

Analyzes CO2 sensor data from multiple sensors:

* Sorts the data by timestamp to ensure rolling window calculations work correctly.
* Interpolates to fill gaps in sensor readings. (The sensors report new values at different times.)
* Applies a rolling mean (moving average) with a 7 minute window to reduce sensor noise.
* Computes comparison metrics between sensor pairs:
  * Count of paired points after discarding leading gaps
  * DC offset (average difference)
  * Tracking variation STD (sample standard deviation of differences, insensitive to the DC offset)
  * Pearson correlation coefficient

## How to Run It

Run the Marimo notebook editor in the Antigravity or VS Code IDE:

* Install the Marimo extension from the marketplace.
* Click the Ⓜ️ Marimo button at the top of the VS Code/Antigravity window.

Run the Marimo notebook editor in a browser:

```bash
uv run marimo edit main.py --mcp --port 10082 --no-token
```

and configure <http://127.0.0.1:10082/mcp/server> in `~/.gemini/config/mcp_config.json` as an MCP server to the IDE's LLM Agent (Agent tab, ... menu, MCP Servers, edit, Manage MCP Servers, View Raw Config).

Run the notebook as a web app:

```bash
marimo run main.py
```

Command line script:

```bash
uv run main.py

uv run main.py data/baseline2_CO2_data_2026-05-22_2259.csv
```

## Input data

See [collected data files](data/) `*.csv` and their notes `*.md`. [data/baseline_2026-05-20+_notes.md](data/baseline_2026-05-20+_notes.md) explains the experiment setup and actions.

### CSV data format example

```csv
"DateTime","0A","0B","10A","10B","20A","20B","20C","30A","30B","40A","40B","40C","40D","40E","40F","SP1","SP2","SP3"
"2026-05-20 17:55:18",,,,,,,,,,,,,,,,,701,
"2026-05-20 17:55:36",,,778,791,863,,,,,,,,800,,819,,,
"2026-05-20 17:55:37",809,,,,,,,,,,,,,734,,,,
```

## Output

See [collected output files](out/).

## Images

See [collected images](images/) e.g. graphs from the Iconia dashboard.
