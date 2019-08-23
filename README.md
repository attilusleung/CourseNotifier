# CourseNotifier

A script that track the open status of courses and notifies you of any changes through SMS.

Currently tracks courses specified in a config file and sends an SMS message
through the twilio API whenever there are changes to the tracked courses.

The script is meant for personal use only and not meant to be deployed on a large scale.

## Setup
As the script uses Twilio, a Twilio account must be setup before running the script.

After setting up the Twilio account:

1. Configure secrets

   Within the secrets folder, create a file named `secrets.ini`. Place the following
   information within the file:

   ```ini
   [TWILIO]
   SID = YOUR_TWILIO_SID
   AUTH = YOUR_TWILIO_AUTH_TOKEN
   SOURCE_PHONE = YOUR_TWILIO_PHONE_NUMBER
   DEST_PHONE = PHONE_NUMBER_TO_SEND_NOTIFICATIONS_TO
   ```

2. Setup `pipenv`

   Make sure you have pipenv installed (`sudo pacman -S pipenv` or `sudo apt-get install pipenv`).

   Run `pipenv install` to setup a virtual environment and install all dependencies.

   Alternatively, you can install dependencies using the `requirements.txt` (`pip install -r requirements.txt`).

3. Run the script (`pipenv run ./main.py`)

   It is recommended to run the script detached from a shell (`nohup ./main.py &`) or in the background through `systemd`.

## Usage
Classes can be tracked by modifying `config.ini`

Specify the current semester by modifying `Semester` under the `Settings` section header:
```ini
[SETTINGS]
Semester = FA19
```

Track specific classes by adding a new section header with the subject code.
Don't forget to add a space between the subject and the number.
Specify the specific sections tracked with the component and a json array of
section numbers to be tracked (surrounded by double quotes) as key-value pairs.

```ini
[CS 3110]
LEC = ["001"]
DIS = ["204, "205"]
```

If the script is already running, it will be automatically restarted and a
SMS message will be sent to you whenever there are changes within the open
status of the courses tracked.
