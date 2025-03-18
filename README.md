## Python setup

1. Ensure you have a proper Python environment. If you do not have the
   packages required in your default environment, consider creating a
   virtual one:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Update your Python path

   ```bash
   export PYTHONPATH=`git rev-parse --show-toplevel`:$PYTHONPATH
   ```

3. (Optional) Set the Python log level:

   ```bash
   export PYTHONLOGLEVEL=info
   ```

   The default level is "warning", however most of the scripts produce
   useful information at "info". Valid values come from the [Python
   logging
   module](https://docs.python.org/3/library/logging.html#logging-levels).

## Assess response times

### Parse raw data

#### From Google

Data can be parsed directly from a Google Sheet:
```bash
GOOGLE_API_KEY=... python src/parse-times.py \
	--sheet-id GSHEET_ID \
	--result-tab X > data.csv
```
where:
* `GOOGLE_API_KEY` is your Google Developer API key; this can also be
  specified as an option to `parse-times.py` (`--google-api-key`).
* `GSHEET_ID` is the Google Sheet ID
* `X` is the tab containing the data

Note that `--result-tab` can be specified more than once to combine
data potentially spread across tabs.

#### From a local file

Data can also be parsed from a local CSV download of a Google Sheet:
```bash
python src/parse-times.py --data-file /path/to/data.csv > data.csv
```

In this case `--result-tab` is not required; however specifying which
tab the CSV came from will make later plotting more readable.

### Plot the results

```bash
python src/plot-times.py --output results.png < data.csv
```
where `data.csv` is the output of the data parsing script.

Some things to keep in mind:
* Call durations often have a long tail. Consider cutting off the
  graph at a reasonable duration to better view the distribution:
  using `--cutoff 30` with `src/plot-times.py`, for example.
* The two steps -- parsing and then plotting -- have been presented
  separately for clarity. They can also be piped together to
  facilitate scripting:
  ```bash
  python src/parse-times.py ... | python src/plot-times.py ...
  ```
