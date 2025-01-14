

## Run

### Python setup

1. Ensure you have a proper Python environment. If you do not have the
   packages required in your default environment, consider creating a
   virtual one:

   ```bash
   $> python -m venv venv
   $> source venv/bin/activate
   $> pip install -r requirements.txt
   ```

2. Update your Python path

   ```bash
   $> export PYTHONPATH=`git rev-parse --show-toplevel`:$PYTHONPATH
   ```

3. (Optional) Set the Python log level:

   ```bash
   $> export PYTHONLOGLEVEL=info
   ```

   The default level is "warning", however most of the scripts produce
   useful information at "info". Valid values come from the [Python
   logging
   module](https://docs.python.org/3/library/logging.html#logging-levels).

### Configuration

Configuration is specified via a Microsoft Windows INI file. Create an
INI file with the following structure:

```
[DEFAULT]

max_poll_time: 1

[GOOGLE]

sheet_id:
sheet_tab_source: prompts
sheet_tab_target: response
api_key:

[GLIFIC]

phone:
password:
flow_id:
contact_id:
```

### Prompt

Assuming your configuration file is called `config.ini`:

```bash
$> python run-flows.py < config.ini
```

If you already have a Glific authentication token, you can forgo the
authentication step by providing the token at the command line. Use
the `--glific-token` to use this feature.
