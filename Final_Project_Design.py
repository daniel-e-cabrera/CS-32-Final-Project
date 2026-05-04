from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import openrouteservice
import passiogo

api_key = input("Enter your OpenRouteService API key: ").strip()
client = openrouteservice.Client(key=api_key)
system = passiogo.getSystemFromID(831)

#Segment Times
route_segment_times = {"Quad Express": [1.0, 2.0, 0.5, 10.0, 5.0, 2.0, 3.0], "SEC Express": [2.0, 3.0, 7.0, 3.0, 3.0, 4.0, 6.0, 3.0, 5.0], "Quad Yard Express": [2.0, 10.0, 1.0, 1.2, 1.0, 4.0]}

#Helper Functions
def will_make_shuttle(current_time, walking_minutes, shuttle_arrival_time):
    return current_time + timedelta(minutes=walking_minutes) <= shuttle_arrival_time

def recommended_leave_time(walking_minutes, shuttle_arrival_time):
    return shuttle_arrival_time - timedelta(minutes=walking_minutes)

def find_next_shuttle(current_time, shuttle_times):
    for t in sorted(shuttle_times):
        if t > current_time:
            return t
    return None

def get_walking_time(start_coords, end_coords):
    route = client.directions(coordinates=[start_coords, end_coords],profile='foot-walking')
    return route['routes'][0]['summary']['duration'] / 60

#Shuttle Tracking
def get_next_shuttle_from_passio(system, pickup, destination, current_time):
    now = current_time
    best_eta = None
    best_vehicle = None
    routes = system.getRoutes()
    # only routes that contain BOTH stops
    valid_routes = []
    for r in routes:
        try:
            stop_names = [s.name for s in r.getStops()]
            if pickup.name in stop_names and destination.name in stop_names:
                valid_routes.append(r)
        except:
            continue
    def get_stop_index(route, stop):
        for i, s in enumerate(route.getStops()):
            if s.name == stop.name:
                return i
        return None
    def get_vehicle_segment(route, vehicle):
        stops = route.getStops()
        lat = getattr(vehicle, "longitude", None)
        if lat is None:
            return None
        lat = float(lat)
        best_seg = None
        best_dist = float("inf")
        for i in range(len(stops)):
            s1 = stops[i]
            s2 = stops[(i + 1) % len(stops)]
            mid_lat = (s1.latitude + s2.latitude) / 2
            dist = min(
                abs(lat - s1.latitude),
                abs(lat - s2.latitude),
                abs(lat - mid_lat))
            if dist < best_dist:
                best_dist = dist
                best_seg = (i, (i + 1) % len(stops))
        return best_seg
    vehicles = system.getVehicles()
    # sort by proximity
    vehicles = sorted(vehicles, key=lambda v: abs(float(getattr(v, "longitude", 999)) - pickup.latitude))[:3]
    for v in vehicles:
        lat = getattr(v, "longitude", None)
        if lat is None:
            continue
        route = next((r for r in valid_routes if getattr(v, "routeName", "").strip() == r.name.strip()), None)
        if route is None:
            continue
        stops = route.getStops()
        total_stops = len(stops)
        pickup_idx = get_stop_index(route, pickup)
        dest_idx = get_stop_index(route, destination)
        segment = get_vehicle_segment(route, v)
        if pickup_idx is None or dest_idx is None or segment is None:
            continue
        seg_start, seg_end = segment
        # distance to pickup
        if seg_end <= pickup_idx:
            dist_to_pickup = pickup_idx - seg_end
        else:
            dist_to_pickup = (total_stops - seg_end) + pickup_idx
        # distance pickup to destination
        if pickup_idx <= dest_idx:
            dist_pickup_to_dest = dest_idx - pickup_idx
        else:
            dist_pickup_to_dest = (total_stops - pickup_idx) + dest_idx
        # skip if wrong direction
        if dist_pickup_to_dest > total_stops / 2:
            continue
        segment_times = route_segment_times.get(route.name)
        if not segment_times or len(segment_times) != total_stops:
            eta_minutes = (dist_to_pickup + dist_pickup_to_dest) * 0.8
        else:
            eta_minutes = 0
            i = seg_end
            # travel to pickup
            while i != pickup_idx:
                eta_minutes += segment_times[i]
                i = (i + 1) % total_stops
            # travel pickup → destination
            while i != dest_idx:
                eta_minutes += segment_times[i]
                i = (i + 1) % total_stops
            # partial segment correction
            current_seg = segment_times[seg_end]
            eta_minutes -= current_seg * 0.30
            eta_minutes = max(0.5, eta_minutes)
        if best_eta is None or eta_minutes < best_eta:
            best_eta = eta_minutes
            best_vehicle = v.name
    if best_eta is not None:
        return [{"time": now + timedelta(minutes=best_eta),"vehicle": best_vehicle}]
    return []

#Evaluation
def evaluate_stop(system, start_coords, pickup, destination, current_time):
    walking_minutes = get_walking_time(start_coords, (pickup.longitude, pickup.latitude))
    shuttles = get_next_shuttle_from_passio(system, pickup, destination, current_time)
    next_shuttle = None
    next_vehicle = None
    for s in shuttles:
        if s["time"] > current_time:
            next_shuttle = s["time"]
            next_vehicle = s["vehicle"]
            break
    if next_shuttle is None:
        next_shuttle = current_time + timedelta(minutes=45)
        next_vehicle = "Unknown"
    leave_time = recommended_leave_time(walking_minutes, next_shuttle)
    can_make_it = will_make_shuttle(current_time, walking_minutes, next_shuttle)
    return {
        "pickup": pickup,
        "destination": destination,
        "walking_minutes": walking_minutes,
        "next_shuttle": next_shuttle,
        "vehicle": next_vehicle,
        "leave_time": leave_time,
        "can_make_it": can_make_it
    }

def main():
    locations = {
        "river west": (-71.1200, 42.3700),
        "river east": (-71.1180, 42.3710),
        "river central": (-71.1190, 42.3720),
        "lamont": (-71.1169, 42.3722),
        "science center": (-71.1169, 42.3764)}

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
    print("─" * 32)
    print("🚍 Shuttle Planner")
    print("─" * 32)
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
    print("─" * 32)

if __name__ == "__main__":
    main()
