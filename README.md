# CS-32-Final-Project
Final project with Daniel Cabrera and Marielle Howlett

## Our Plan - Original
For Step 4, we chose the “Shuttle Walk Timing Calculator” as our final project because it is the most computationally interesting subtask, and we both live in the quad. Specifically, our focus is on building a model that determines whether a user will make a shuttle based on walking time and expected shuttle arrival time, and then recommends when a user should leave to avoid missing it. Importantly, PassioGo already uses GPS data to track shuttle locations in real time, and we believe this data would be accessible to us. Additionally, we would use Google Maps data in order to calculate walking time estimates. The computational core subtask of this project works by comparing two key values: how long it takes a user to reach the shuttle stop and when the shuttle is expected to arrive. First, our project estimates walking time (e.g., 6 minutes) using Google Maps data. Then, using PassioGo GPS data, it estimates the shuttle’s arrival time. The system then directly compares these values to determine whether the user will arrive before the shuttle and calculates a recommended departure time (e.g., leave within 2 minutes (1:58PM) to make it on time). If it is not feasible for the user to make the current shuttle, the system will recommend the next available shuttle and provide a corresponding departure time.

## Updates 4/22/26
  Our original plan included using Passiogo and Google Maps data, allowing the user to input their current location and the walking destination to their bus stop. Our code was to then ideally return the estimated travel time needed to make the bus, reporting to the user whether they would make it to the bus or not. 
  As we adjusted our code, we made minor changes to the methods we used to pull data. For starters, instead of Google Maps, we are now using Open Route Service, a free API tool that must be installed on the user's end. Additionally, a user will need to obtain a personal API key for the platform. It has almost the same function as Google Maps, however, it is a free source that users can access.
  PassioGo is a rather secure database, so it is not likely that we would be able to access their data. To circumvent this, we used scheduled bus times. The morning shuttles are typically consistent every five minutes, so we decided to focus on one shuttle arriving at the Widener gate, going to the quad, with service time beginning at 4:20 P.M. We needed to manually enter the scheduled bus times, as well as specific start locations such as "River East, River West, and Lamont". 
  We used Generative AI to assist us in writing the code regarding the API package and key download for the Open Route Service. Aside from any subtle stylistic choices made to improve the program's efficiency, debugging code, or unknown syntax, such as the change from military to standard time, the rest of the code was written by us. 

## Updated Description Of What Our Project Does And Instructions For Running Our Code 4/22/26
The “Shuttle Walk Timing Calculator” is a model that determines whether a user will make a shuttle based on walking time (using Open Route Service) and the Quad-Yard Shuttle set schedule, and then recommends when a user should leave to avoid missing it.

When usiing our calculator, the question asked will be: 
Enter your current location (River West, River East, River Central, Science Center, or Lamont):

After you have input one of these options, the shuttle walk timing calculator will run and give an output that looks like this: 
(example)
--- Shuttle Walk Timing Calculator ---
Walking time to Widener Gate: 1.8 minutes
Next shuttle: 07:40 PM
Leave by: 07:38 PM
Will you make it? Yes
