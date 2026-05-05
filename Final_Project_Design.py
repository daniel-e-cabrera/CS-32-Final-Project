#importing the necessary information to run this code 
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo # this handles time zones, since we're on EST 
import openrouteservice 
import passiogo

# no longer have our personalized key included, now prompts user for their own
api_key = input("Enter your OpenRouteService API key: ").strip() # user must enter their personalized openroute service API key 
client = openrouteservice.Client(key=api_key)
# Specifying that we want Harvard University Passio Go data
system = passiogo.getSystemFromID(831) # 831 is Harvard specific code 

# How long it takes (in minutes) to get from each stop to the next for the three main routes
# these are hard-coded examples of the timing for each stop, may not be accurate depending on traffic 
route_segment_times = {"Quad Express": [1.0, 2.0, 0.5, 10.0, 5.0, 2.0, 3.0], "SEC Express": [2.0, 3.0, 7.0, 3.0, 3.0, 4.0, 6.0, 3.0, 5.0], "Quad Yard Express": [2.0, 10.0, 1.0, 1.2, 1.0, 4.0]}

# Helper Functions
def will_make_shuttle(current_time, walking_minutes, shuttle_arrival_time):
    return current_time + timedelta(minutes=walking_minutes) <= shuttle_arrival_time
    # determines whether the user will get to the shuttle based on when it's arriving, the walking time, and the current time 

def recommended_leave_time(walking_minutes, shuttle_arrival_time):
    return shuttle_arrival_time - timedelta(minutes=walking_minutes)
    # determines the time the user should leave based on when the shuttle is arriving and how long it'll take to get to the stop 

def get_walking_time(start_coords, end_coords):
    route = client.directions(coordinates=[start_coords, end_coords],profile='foot-walking')
    return route['routes'][0]['summary']['duration'] / 60
    # calculates the walking time using start and end coordinates 

# Shuttle Tracking Function
def get_next_shuttle_from_passio(system, pickup, destination, current_time):
    now = current_time
    best_eta = None
    best_vehicle = None
    # Get all routes in the system (Quad Express, SEC Express, etc.)
    routes = system.getRoutes()
    # Filter routes to only those that include both the pickup and destination stops
    valid_routes = []

    for r in routes:
        try:
            # Extract stop names for this route
            stop_names = [s.name for s in r.getStops()]
            # Only keep routes where both stops appear
            if pickup.name in stop_names and destination.name in stop_names:
                valid_routes.append(r)
        except:
            # Some routes may error out when calling getStops(), so skip them 
            continue

    # Helper function inside our function: Find the index of a stop within a route's stop list
    def get_stop_index(route, stop):
        for i, s in enumerate(route.getStops()):
            if s.name == stop.name:
                return i
        return None  # If stop not found (shouldn't happen if route is valid)

    # Helper function inside our function: estimate which segment (between two stops) the vehicle is currently on
    def get_vehicle_segment(route, vehicle):
        stops = route.getStops()
        # Important Note: PassioGo does not give longitude only latitude. And even then they saved latitude values under longitude variable name
        # Using latitude as a proxy for position.
        lat = getattr(vehicle, "longitude", None)
        if lat is None:
            return None

        lat = float(lat)
        best_seg = None
        best_dist = float("inf")
        # Loop through each pair of consecutive stops (segments)
        for i in range(len(stops)):
            s1 = stops[i]
            s2 = stops[(i + 1) % len(stops)]  # Wrap around for circular routes
            # Midpoint latitude of the segment
            mid_lat = (s1.latitude + s2.latitude) / 2
            # Check how close the vehicle is to either endpoint or midpoint
            # This is a rough approximation since we’re only using one coordinate
            dist = min(abs(lat - s1.latitude), abs(lat - s2.latitude), abs(lat - mid_lat))

            # Keep track of the closest segment
            if dist < best_dist:
                best_dist = dist
                best_seg = (i, (i + 1) % len(stops))  # (start_index, end_index)
        return best_seg

    # Get all active vehicles (buses) in the system
    vehicles = system.getVehicles()
    # Sort vehicles by proximity to pickup (using latitude proxy)
    vehicles = sorted(vehicles,key=lambda v: abs(float(getattr(v, "longitude", 999)) - pickup.latitude))[:3]  # only consider closest 3
    for v in vehicles:
        # Get vehicle position (Passio stores latitude in "longitude")
        lat = getattr(v, "longitude", None)
        if lat is None:
            continue  # skip if no location data

        # Match vehicle to a route that serves both pickup + destination
        route = next((r for r in valid_routes if getattr(v, "routeName", "").strip() == r.name.strip()), None)
        if route is None:
            continue  # skip if route doesn't match

        # Get route structure
        stops = route.getStops()
        total_stops = len(stops)
        # Find positions of pickup and destination in route
        pickup_idx = get_stop_index(route, pickup)
        dest_idx = get_stop_index(route, destination)
        # Determine which segment the bus is currently in
        segment = get_vehicle_segment(route, v)
        # Skip if we can't determine route positions
        if pickup_idx is None or dest_idx is None or segment is None:
            continue

        # Segment = (current_stop_index, next_stop_index)
        seg_start, seg_end = segment
        #Distance to pickup
        if seg_end <= pickup_idx:
            dist_to_pickup = pickup_idx - seg_end
        else:
            dist_to_pickup = (total_stops - seg_end) + pickup_idx
        #Distance: pickup to destination
        if pickup_idx <= dest_idx:
            dist_pickup_to_dest = dest_idx - pickup_idx
        else:
            dist_pickup_to_dest = (total_stops - pickup_idx) + dest_idx
        #Skip if wrong direction
        if dist_pickup_to_dest > total_stops / 2:
            continue

        segment_times = route_segment_times.get(route.name)
        if not segment_times or len(segment_times) != total_stops:
            eta_minutes = (dist_to_pickup + dist_pickup_to_dest) * 0.8
        else:
            eta_minutes = 0
            i = seg_end

            #Travel to pickup
            while i != pickup_idx:
                eta_minutes += segment_times[i]
                i = (i + 1) % total_stops
            #Travel pickup to destination
            while i != dest_idx:
                eta_minutes += segment_times[i]
                i = (i + 1) % total_stops
            #Partial segment correction
            current_seg = segment_times[seg_end]
            eta_minutes -= current_seg * 0.30 #After constant testing, 0.3 gave the most accurate results
            eta_minutes = max(0.5, eta_minutes)

        if best_eta is None or eta_minutes < best_eta:
            best_eta = eta_minutes
            best_vehicle = v.name
    if best_eta is not None:
        return [{"time": now + timedelta(minutes=best_eta),"vehicle": best_vehicle}]
    return []

#Evaluation
def evaluate_stop(system, start_coords, pickup, destination, current_time): # evaluating your trip 
    walking_minutes = get_walking_time(start_coords, (pickup.longitude, pickup.latitude)) # getting the minutes needed to walk 
    shuttles = get_next_shuttle_from_passio(system, pickup, destination, current_time) # grabs shuttles from passiogo data 
    next_shuttle = None # don't know which shuttle you will take 
    next_vehicle = None # don't know what vehicle number it is 

    for s in shuttles: # loop through all shuttle options 
        if s["time"] > current_time: # as soon as you find the first shuttle 
            next_shuttle = s["time"] # mark it's time
            next_vehicle = s["vehicle"] # mark the vehicle 
            break

    if next_shuttle is None: # if no data or no future buses 
        next_shuttle = current_time + timedelta(minutes=45) # predict the next shuttle will come on default time of 45 minutes  
        next_vehicle = "Unknown" # don't know what shuttle it'll be so label generically 

    leave_time = recommended_leave_time(walking_minutes, next_shuttle)
    can_make_it = will_make_shuttle(current_time, walking_minutes, next_shuttle)
    return {"pickup": pickup, "destination": destination, "walking_minutes": walking_minutes, "next_shuttle": next_shuttle, "vehicle": next_vehicle, "leave_time": leave_time, "can_make_it": can_make_it}

def main():
    locations = {
        "river west": (-71.11912226087507, 42.37037685455344),
        "river east": (-71.11512875536995, 42.36888838540238),
        "river central": (-71.11661558789517, 42.371865645063316),
        "lamont": (-71.11514486331022, 42.3729210902698),
        "science center": (-71.11483377519882, 42.377359106968285)}

    print("\nAvailable starting locations:")
    keys = sorted(locations.keys())
    for i, k in enumerate(keys, 1):
        print(f"{i}. {k.title()}")

    choice = int(input("\nEnter number: "))
    start_coords = locations[keys[choice - 1]]
    start_name = keys[choice - 1]
    current_time = datetime.now(ZoneInfo("America/New_York"))
    stops = system.getStops()
    print("\nAvailable stops:")

    for s in stops[:20]:
        print("-", s.name)

    pickup_input = input("\nEnter pickup stop: ").lower()
    destination_input = input("Enter destination stop: ").lower()
    pickup = next((s for s in stops if pickup_input in s.name.lower()), None)
    destination = next((s for s in stops if destination_input in s.name.lower()), None)
    if not pickup or not destination:
        print("Invalid stop.")
        return
        
    result = evaluate_stop(system, start_coords, pickup, destination, current_time)
    print("─" * 35)
    print("🚍 Shuttle Planner")
    print("─" * 35)
    print(f"💨 Leaving: {start_name.title()}")
    print(f"📍 From: {result['pickup'].name}")
    print(f"🎯 To:   {result['destination'].name}\n")
    print(f"🚶 Walk time: {result['walking_minutes']:.1f} min\n")
    print(f"🚌 Next shuttle: {result['next_shuttle'].strftime('%I:%M %p')} (Bus {result['vehicle']})")
    print(f"⏳ Leave by:     {result['leave_time'].strftime('%I:%M %p')}\n")
    if result["can_make_it"]:
        print("✅ You will make it! Have a great day! #GO QUAD")
    else:
        print("❌ You won't make it")
    print("─" * 35)

if __name__ == "__main__":
    main()
