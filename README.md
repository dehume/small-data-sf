# Small Data SF

### Installing dependencies

#### Option 1 (Local): Using `uv`

Ensure [`uv`](https://docs.astral.sh/uv/) is installed following their [official documentation](https://docs.astral.sh/uv/getting-started/installation/).

Create a virtual environment, and install the required dependencies using _sync_:

```bash
uv sync
```

Then, activate the virtual environment:

| OS | Command |
| --- | --- |
| MacOS | ```source .venv/bin/activate``` |
| Windows | ```.venv\Scripts\activate``` |

#### Option 2 (Local): Using `pip`

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment:

| OS | Command |
| --- | --- |
| MacOS/Linux | ```source .venv/bin/activate``` |
| Windows | ```.venv\Scripts\activate``` |

Install the package in editable mode with development dependencies:

```bash
pip install -e .
```

Or install with development dependencies:

```bash
pip install -e ".[dev]"
```

#### Option 3 (Cloud): Github Codespace

Go to Github Codespaces, [https://github.com/codespaces](https://github.com/codespaces):

1. Click “New Codespace”
2. Select repository “dehume/small-data-sf”
3. Select 8 Cores (all other defaults can remain the same)
4. Click “Create Codespace”

Wait ~a minute as the Codespace builds (Prebuild)

### Running Dagster

Start the Dagster UI web server:

```bash
dg dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to see the project.

### Completed code

All of the code for the workshop will go in `src/small_data_workshoop`. If you want to see the completed code `_completed/small_data_workshop`.

### Learn more

To learn more about this template and Dagster in general:

- [Dagster Documentation](https://docs.dagster.io/)
- [Dagster University](https://courses.dagster.io/)
- [Dagster Slack Community](https://dagster.io/slack)
