import sys
from datetime import datetime, timedelta
import requests
from notify_run import Notify
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# --- Settings ---
DEPARTURE = os.getenv("DEPARTURE") # Example stop_area:SNCF:*******
ARRIVAL = os.getenv("ARRIVAL") # Example stop_area:SNCF:*******
CHECK_HOUR = int(os.getenv("CHECK_HOUR", 8)) # Example 8
CHECK_MINUTE = int(os.getenv("CHECK_MINUTE", 0)) # Example 0
# Days to run the script (0=Monday, 6=Sunday)
RUN_ONLY_ON_DAYS = [int(day) for day in os.getenv("RUN_ONLY_ON_DAYS", "0").split(",")]
API_TOKEN = os.getenv("API_TOKEN") 
NOTIFICATION_TOPIC_URL = os.getenv("NOTIFICATION_TOPIC_URL") # Example https://notify.run/your_topic_url

# Create notification handler
notifier = Notify(endpoint=NOTIFICATION_TOPIC_URL)


def should_run_today() -> bool:
    """Return True if today is in the allowed days"""
    return datetime.now().weekday() in RUN_ONLY_ON_DAYS


def get_target_time() -> str:
    """Return the time to check in SNCF API format (yyyymmddTHHMM)"""
    now = datetime.now()
    target = now.replace(hour=CHECK_HOUR, minute=CHECK_MINUTE, second=0, microsecond=0)

    # If target time already passed today, move to tomorrow
    if now > target:
        target += timedelta(days=1)

    return target.strftime("%Y%m%dT%H%M")


def send(message: str):
    """Send a notification and also print it"""
    try:
        notifier.send(message)
        print("Sent:", message)
    except Exception as e:
        print("Notification failed:", e)


def check_train_disruption():
    """Call SNCF API and check for disruptions"""
    url = "https://api.sncf.com/v1/coverage/sncf/journeys"
    params = {
        "from": DEPARTURE,
        "to": ARRIVAL,
        "datetime": get_target_time(),
        "datetime_represents": "departure",
        "count": "1",
        "filter": "physical_mode=Train",
        "data_freshness": "realtime"
    }

    response = requests.get(url, params=params, auth=(API_TOKEN, ""))
    print("API response:", response.status_code)

    if response.ok:
        data = response.json()
        disruptions = data.get("disruptions", [])

        if disruptions:
            message = f"⚠️ Train disruption:\n{disruptions[0].get('message', 'No details')}"
            send(message)
        else:
            print("✅ No disruptions.")
            # send("No disruption")
    else:
        send(f"❌ SNCF API error: {response.status_code}")


def main():
    if not should_run_today():
        print("Not running today.")
        sys.exit(0)

    check_train_disruption()


if __name__ == "__main__":
    main()
