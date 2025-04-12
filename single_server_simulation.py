import math
import random 

Q_LIMIT = 100  # Max no of customers in the queue
BUSY = 1  # Server is busy
IDLE = 0  # Server is idle

#Global variables
next_event_type = 0  
num_custs_delayed = 0  # No. of customers who have been delayed
num_delays_required = 0  # No. of customers to be served before simulation ends
num_events = 2  # Number of event types: arrival and departure
num_in_q = 0  # Current queue length
server_status = IDLE  # Start with server idle

# Statistical counters
area_num_in_q = 0.0  # Cumulative queue length over time
area_server_status = 0.0  # Cumulative busy time of server

mean_interarrival = 0.0  # Mean interarrival time
mean_service = 0.0  # Mean service time
sim_time = 0.0  # Simulation clock

time_last_event = 0.0  # Time of last event
total_of_delays = 0.0  # Sum of customer delays

# Queue and event lists
time_arrival = [0.0] * (Q_LIMIT + 1)  # Stores the arrival time of customers 
time_next_event = [0.0, 0.0, 1.0e+30]  # Schedules time for next event

def initialize():
    #Initializes the simulation.
    global sim_time, server_status, num_in_q, time_last_event
    global num_custs_delayed, total_of_delays, area_num_in_q, area_server_status, time_next_event
    
    sim_time = 0.0 #Initalized the clock to 0
    server_status = IDLE
    num_in_q = 0
    time_last_event = 0.0
    num_custs_delayed = 0
    total_of_delays = 0.0
    area_num_in_q = 0.0
    area_server_status = 0.0
    
    #Schedules the first arrival time
    time_next_event[1] = sim_time + expon(mean_interarrival) 
    time_next_event[2] = 1.0e+30  # No departure yet so it's set to a large number

def timing():
    # Determines what is the next event is and advances simulation clock based on it.
    global sim_time, next_event_type
    
    min_time_next_event = float('inf')
    next_event_type = 0

    # Find next event by looping through the arrival and depature events to see which is smaller
    for i in range(1, num_events + 1):
        if time_next_event[i] < min_time_next_event:
            min_time_next_event = time_next_event[i]
            next_event_type = i
    #If there's no scheduled event
    if next_event_type == 0:
        outfile.write(f"\nEvent list empty at time {sim_time}\n")
        exit(1)
    #If there is, update the simulation time to the next event
    sim_time = min_time_next_event

def arrive():
    #Handles arrival event.
    global num_in_q, server_status, num_custs_delayed, total_of_delays, time_next_event

    # Schedule next arrival
    time_next_event[1] = sim_time + expon(mean_interarrival)
    
    if server_status == BUSY:
        # Server busy, customer joins queue
        num_in_q += 1
        if num_in_q > Q_LIMIT: #If the number of customers in the queue exceeds the queue limit
            outfile.write(f"\nOverflow of the queue at time {sim_time}\n")
            exit(2)
        time_arrival[num_in_q] = sim_time #Records the arrival event
    else:
        # Server idle, start service immediately
        delay = 0.0
        total_of_delays += delay
        num_custs_delayed += 1
        server_status = BUSY
        time_next_event[2] = sim_time + expon(mean_service) #Schedule a depature event

def depart():
    #Handles departure event.
    global num_in_q, server_status, num_custs_delayed, total_of_delays, time_next_event

    if num_in_q == 0:
        # Queue is empty, so the server is idle
        server_status = IDLE
        time_next_event[2] = 1.0e+30
    else:
        # Queue isn't empty, so the next customer is served
        delay = sim_time - time_arrival[1]
        total_of_delays += delay
        num_custs_delayed += 1
        time_next_event[2] = sim_time + expon(mean_service) #Depature event

        # Shift queue forward after removing the first customer from the queue
        for i in range(1, num_in_q):
            time_arrival[i] = time_arrival[i + 1]
        num_in_q -= 1

def report():
    #Generates final simulation report.
    output_buffer = []
    output_buffer.append("\nSingle-server queueing system\n")
    output_buffer.append(f"\nMean interarrival time: {mean_interarrival:.3f} minutes\n")
    output_buffer.append(f"Mean service time: {mean_service:.3f} minutes\n")
    output_buffer.append(f"Total number of customers: {num_custs_delayed}\n")
    output_buffer.append(f"\nAverage delay in queue: {total_of_delays / num_custs_delayed:.3f} minutes\n")
    output_buffer.append(f"Average number in queue: {area_num_in_q / sim_time:.3f}\n")
    output_buffer.append(f"Server utilization: {area_server_status / sim_time:.3f}\n")
    output_buffer.append(f"Time simulation ended: {sim_time:.3f} minutes\n")
    #Writes all the collected results to the output file at once.
    outfile.write("".join(output_buffer))

def update_time_avg_stats():
    #Updates cumulative statistics.
    global area_num_in_q, area_server_status, time_last_event
    time_since_last_event = sim_time - time_last_event #Finds out how much time passed since last event
    time_last_event = sim_time

    area_num_in_q += num_in_q * time_since_last_event
    area_server_status += server_status * time_since_last_event

def expon(mean):
    #Generates exponentially distributed random numbers
    return -mean * math.log(random.random())

def main():
    global mean_interarrival, mean_service, num_delays_required, outfile, num_events

    # Read input values
    with open("./mm1.in", "r") as infile:
        mean_interarrival, mean_service, num_delays_required = map(float, infile.readline().split())
        num_delays_required = int(num_delays_required)
    #opens the output file in write mode
    outfile = open("mm1.out", "w")

    initialize()
    #Runs the main simulation loop until the desired number of customers have been served.
    while num_custs_delayed < num_delays_required:
        timing()
        update_time_avg_stats()
        if next_event_type == 1:
            arrive()
        elif next_event_type == 2:
            depart()

    report()
    outfile.close()

if __name__ == "__main__":
    main()
