from datetime import datetime, timedelta
import openrouteservice

# Initialize API client
client = openrouteservice.Client(key="YOUR_API_KEY_HERE")


def will_make_shuttle(current_time, walking_minutes, shuttle_arrival_time):
    arrival_time = current_time + timedelta(minutes=walking_minutes)
    return arrival_time <= shuttle_arrival_time


def recommended_leave_time(walking_minutes, shuttle_arrival_time):
    return shuttle_arrival_time - timedelta(minutes=walking_minutes)


def find_next_shuttle(current_time, shuttle_times):
    shuttle_times = sorted(shuttle_times)
    for shuttle_time in shuttle_times:
        if shuttle_time > current_time:
            return shuttle_time
    return None


def get_walking_time(start_coords, end_coords):
    route = client.directions(
        coordinates=[start_coords, end_coords],
        profile='foot-walking'
    )

    seconds = route['routes'][0]['summary']['duration']
    return seconds / 60


def main():
    # Map user input to coordinates
    locations = {
        "yard": (-71.1167, 42.3770),
        "quad": (-71.1246, 42.3803),
        "science center": (-71.1150, 42.3760)
    }

    user_location = input("Enter your current location (yard, quad, etc): ").lower()
    destination_stop = input("Enter your destination stop: ").lower()

    if user_location not in locations or destination_stop not in locations:
        print("Invalid location. Try: yard, quad, science center")
        return

    start_coords = locations[user_location]
    end_coords = locations[destination_stop]

    current_time = datetime.now()

    # ✅ Get walking time from API
    walking_minutes = get_walking_time(start_coords, end_coords)

    # 🚍 MOCK shuttle times (for now)
    shuttle_times = [
        current_time + timedelta(minutes=5),
        current_time + timedelta(minutes=15),
        current_time + timedelta(minutes=30),
    ]

    next_shuttle = find_next_shuttle(current_time, shuttle_times)

    print("\n--- Shuttle Info ---")
    print(f"Walking time: {walking_minutes:.1f} minutes")

    if next_shuttle:
        leave_time = recommended_leave_time(walking_minutes, next_shuttle)
        can_make_it = will_make_shuttle(current_time, walking_minutes, next_shuttle)

        print("Next shuttle:", next_shuttle.strftime("%H:%M:%S"))
        print("Leave by:", leave_time.strftime("%H:%M:%S"))
        print("Will you make it?", "Yes" if can_make_it else "No")
    else:
        print("No more shuttles available today.")


if __name__ == "__main__":
    main()