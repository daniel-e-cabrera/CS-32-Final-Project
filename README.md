#CS-32-Final-Project
Final project with Daniel Cabrera and Marielle Howlett

##Our Plan
For Step 4, we chose the “Shuttle Walk Timing Calculator” as our final project because it is the most computationally interesting subtask, and we both live in the quad. Specifically, our focus is on building a model that determines whether a user will make a shuttle based on walking time and expected shuttle arrival time, and then recommends when a user should leave to avoid missing it. Importantly, PassioGo already uses GPS data to track shuttle locations in real time, and we believe this data would be accessible to us. Additionally, we would use Google Maps data in order to calculate walking time estimates. The computational core subtask of this project works by comparing two key values: how long it takes a user to reach the shuttle stop and when the shuttle is expected to arrive. First, our project estimates walking time (e.g., 6 minutes) using Google Maps data. Then, using PassioGo GPS data, it estimates the shuttle’s arrival time. The system then directly compares these values to determine whether the user will arrive before the shuttle and calculates a recommended departure time (e.g., leave within 2 minutes (1:58PM) to make it on time). If it is not feasible for the user to make the current shuttle, the system will recommend the next available shuttle and provide a corresponding departure time.




