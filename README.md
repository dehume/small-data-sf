# Small Data SF

### Installing dependencies

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
