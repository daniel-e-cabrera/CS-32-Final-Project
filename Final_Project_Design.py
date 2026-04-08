from datetime import datetime, timedelta
# datetime: Used to work with dates AND times
# timedelta: Represents a duration of time (e.g., days, hours, minutes)


def will_make_shuttle(current_time, walking_minutes, shuttle_arrival_time):
    """Determines if user will make the shuttle"""

    arrival_at_shuttle_stop = current_time + timedelta(minutes = walking_minutes)
    return arrival_at_shuttle_stop <= shuttle_arrival_time
    #forgot to mention in video: only return if arrival_at_shuttle_stop is equal to or less than shuttle_arrival_time 
    #because we don't want to arrive after the shuttle has arrived 


def recommended_leave_time(walking_minutes, shuttle_arrival_time):
    """Calculates when the user should leave to catch the shuttle"""

    return shuttle_arrival_time - timedelta(minutes = walking_minutes)


def find_next_shuttle(current_time, shuttle_times):
    """Finds the next available shuttle after current time"""

    for shuttle_time in shuttle_times:
        if shuttle_time > current_time:
            return shuttle_time
            #forgot to mention in video: return this shutle_time cause it's useful to us
    return None
    #forgot to mention in video: if the current time is after the shuttle_time return None cause it is not useful to us


def main():
   current_time = datetime.now() 
    # extract current time 
    
    #Google Maps
    # import googlemaps data

    # Ask user for their current location
    user_location = input("Enter your current location: ")

    # Ask user which shuttle stop they want to go to
    destination_stop = input("Enter your desired shuttle stop: ")
    # need to remember that all shuttle stops are not on google maps, so we will need to designate with coordinates accordingly

    # Utilize google maps to compute travel time to stop 

    # extract walking directions from user_location to destination_stop for the user to use 
    # directions = using google maps(user_location, destination_stop)

    # using the computed google maps time, extract the value to tell the user how long travel would take
    # walking_minutes = directions[0]["legs"][0]["duration"]["value"] / 60

    #Passio Go
    # need to extract information from Passio Go

    # Get shuttle locations and arrival predictions
    # shuttle_data = response from Passio Go

    # Extract arrival times for the selected destination_stop
    # shuttle_times = extract times for selected stop(shuttle_data, destination_stop)

    # next_shuttle = find the next shuttle(current_time, shuttle_times) 

    # if next_shuttle exists:
    #     leave_time = recommended_leave_time(walking_minutes, next_shuttle)
    #     can_make_it = will_make_shuttle(current_time, walking_minutes, next_shuttle)

    #     print results to user:
    #         - next shuttle arrival time
    #         - when they should leave
    #         - whether they will make it

    # else:
    #     print("No more shuttles available today.")


if __name__ == "__main__":
    main()