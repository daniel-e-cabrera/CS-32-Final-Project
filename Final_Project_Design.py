from datetime import datetime, timedelta
#importing openrouteservice that we installed 
import openrouteservice

# Initialize API client
client = openrouteservice.Client(key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImU5N2RkYWJiMjQ1NDRjNGM5M2E1Nzk5ZTU4ZGNlNjBhIiwiaCI6Im11cm11cjY0In0=")


def will_make_shuttle(current_time, walking_minutes, shuttle_arrival_time):
    arrival_time = current_time + timedelta(minutes=walking_minutes)
    return arrival_time <= shuttle_arrival_time


def recommended_leave_time(walking_minutes, shuttle_arrival_time):
    return shuttle_arrival_time - timedelta(minutes=walking_minutes)


def find_next_shuttle(current_time, shuttle_times):
    for shuttle_time in sorted(shuttle_times):
        if shuttle_time > current_time:
            return shuttle_time
    return None


def get_walking_time(start_coords, end_coords):
    route = client.directions(coordinates=[start_coords, end_coords], profile='foot-walking')

    seconds = route['routes'][0]['summary']['duration']
    return seconds / 60


#function that hard codes the times that the shuttle is at Widener Gate
def shuttle_schedule(current_time):
    #creating an empty dictionary to then put the times into
    shuttle_times = []

    # Afternoon schedule
    #the first shuttle comes at 4:20PM 
    start1 = current_time.replace(hour=16, minute=20, second=0, microsecond=0)
    #the last shuttle comes at 7:50PM
    end1 = current_time.replace(hour=19, minute=50, second=0, microsecond=0)

    current = start1
    while current <= end1:
        if current > current_time:
            shuttle_times.append(current)
        current += timedelta(minutes=25)

    # Evening schedule
    #first shuttle of the evening schedule comes at 8:40PM
    start2 = current_time.replace(hour=20, minute=40, second=0, microsecond=0)
    #last shuttle of the evening schedule comes at 12:20AM
    end2 = (current_time + timedelta(days=1)).replace(hour=0, minute=20, second=0, microsecond=0)

    current = start2
    while current <= end2:
        if current > current_time:
            shuttle_times.append(current)
        current += timedelta(minutes=20)

    return sorted(shuttle_times)


def main():
    user_location = input(
        "Enter your current location (River West, River East, River Central, Science Center, or Lamont): ").lower()

    destination_stop = "widener gate"
    #possible locations to be starting from
    #will add more 
    locations = {"river west": (-71.1200, 42.3700), "river east": (-71.1180, 42.3710), "river central": (-71.1190, 42.3720), "lamont": (-71.1169, 42.3722), "science center": (-71.1169, 42.3764), "widener gate": (-71.1165, 42.3734)}

    if user_location not in locations:
        print("Invalid location. Try: River West, River East, River Central, Science Center or Lamont")
        return

    start_coords = locations[user_location]
    end_coords = locations[destination_stop]
    #Debugging current time: For some reason my current_time was four hours ahead
    current_time = datetime.now() - timedelta(hours=4)

    # Get walking time from API
    walking_minutes = get_walking_time(start_coords, end_coords)

    shuttle_times = shuttle_schedule(current_time)

    next_shuttle = find_next_shuttle(current_time, shuttle_times)
    print("\n--- Shuttle Calculator ---")
    print(f"Walking time to Widener Gate: {walking_minutes:.1f} minutes")

    if next_shuttle:
        leave_time = recommended_leave_time(walking_minutes, next_shuttle)
        can_make_it = will_make_shuttle(current_time, walking_minutes, next_shuttle)

        print("Next shuttle:", next_shuttle.strftime("%I:%M %p"))
        print("Leave by:", leave_time.strftime("%I:%M %p"))
        print("Will you make it?", "Yes" if can_make_it else "No")
    else:
        print("No more shuttles available today.")


if __name__ == "__main__":
    main()