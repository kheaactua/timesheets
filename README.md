# Download YAST Timesheet Records

Simple script to interact with the Yast python API.  Specifically, to download all records from Yast before it's shutdown.

# Usage

First, prepare a `secret.json` file that contains your Yast login credentials in your execution directory:

```json
{
	"login": "myemail@myemail.com",
	"password", "password"
}
```

Then, run the python script:
```sh
python3 download_records.py
```

All your available records will be output in JSON format.
