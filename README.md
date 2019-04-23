# Download YAST Timesheet Records

Simple script to interact with the Yast python API.  Specifically, to download all records from Yast before it's shutdown.

# Usage

First, prepare a `secret.json` file that contains your Yast login credentials in your execution directory:

```json
{
	"login": "myemail@myemail.com",
	"email": "myemail@myemail.com",
	"User": "My Name",
	"password", "password"
}
```

Then, run the python script:
```sh
echo "Output results in a JSON format"
python3 download_records.py --json && cat yast.json

echo "Ouput results in a format that can be imported to Toggl"
python3 download_records.py --json && cat yast.json
```

# Disclaimer

This project was written as quickly as I could, it is not an example of good code by any means. :)
