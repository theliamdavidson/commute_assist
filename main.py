import requests
from config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, TOKEN_URL, API_BASE_URL, GEAR_ID

# store the updated access token
ACCESS_TOKEN = None


def refresh_access_token():
    """
    refresh the access token using the refresh token.
    """
    global ACCESS_TOKEN
    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
        },
    )

    if response.status_code == 200:
        token_data = response.json()
        ACCESS_TOKEN = token_data["access_token"]
        print("Access token refreshed successfully.")
        print(f"New access token: {ACCESS_TOKEN}")
    else:
        print(f"Error refreshing token: {response.status_code}, {response.text}")


def get_most_recent_activity():
    """
    fetche the most recent activity using the refreshed access token.
    """
    if not ACCESS_TOKEN:
        refresh_access_token()

    url = f"{API_BASE_URL}/athlete/activities"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        activities = response.json()
        if activities:
            return activities[0]  # Most recent activity
        else:
            print("No activities found.")
            return None
    else:
        print(f"Error fetching activities: {response.status_code}, {response.text}")
        return None

def update_activity(activity_id, gear_id, commute=False, mute=False):
    """
    Updates an activity's gear and commute status, and prints the bike's total mileage (for help with chain waxing).
    """
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    # Prepare the data to update
    update_data = {}
    if gear_id:
        update_data["gear_id"] = gear_id
    if commute:
        update_data["commute"] = True
    if mute:
        update_data["hide_from_home"] = True

    # update request for the activity
    response = requests.put(url, headers=headers, json=update_data)

    if response.status_code == 200:
        print(f"Activity {activity_id} updated successfully.")
        
        # get the bikes total mileage from the response. can add other fun things here later
        activity_data = response.json()
        
        if "gear" in activity_data:
            gear_name = activity_data["gear"]["nickname"] or activity_data["gear"]["name"]
            total_mileage = activity_data["gear"]["converted_distance"]
            print(f"Updated gear: {gear_name}")
            print(f"Total mileage on {gear_name}: {total_mileage} miles ({total_mileage*1.609} km)")
        else:
            print("Gear information not included")

        with open("debug.txt", "a") as debug_file:
            debug_file.write(f"Activity ID: {activity_id}\n")
            debug_file.write(f"Update Data Sent: {update_data}\n")
            debug_file.write(f"Response Status: {response.status_code}\n")
            debug_file.write(f"Response Text: {response.text}\n")
            debug_file.write("=" * 50 + "\n")
    else:
        print(f"Error updating activity: {response.status_code}")
        print(f"Response: {response.text}")



def main():
    # refresh the token first 
    refresh_access_token()

    # get the most recent activity
    activity = get_most_recent_activity()
    if not activity:
        return

    # mark the activity as a commute, mute, and change bike
    activity_id = activity["id"]
    print(f"Most recent activity ID: {activity_id}, Name: {activity['name']}")
    update_activity(activity_id, GEAR_ID, True)


if __name__ == "__main__":
    main()
