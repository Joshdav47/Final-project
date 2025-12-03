import heapq
import random
import itertools

# Define speed mapping
SPEED_MAP = {
    "fast": 1,
    "medium": 2,
    "slow": 3
}

# Unique event counter
counter = itertools.count()

# Define class for Customer
class Customer():
    def __init__(self, customer_id, customer_type, arrived_time, service_start_time=0, patience=0, has_appointment=False):
        self.id = customer_id
        self.type = customer_type
        self.arrived = arrived_time
        self.service_start_time = service_start_time
        self.patience = patience
        self.has_appointment = has_appointment

# Define class for Teller
class Teller():
    def __init__(self, teller_id, speed_category, busy_until=0, total_service_time=0, idle_time=0):
        self.id = teller_id
        self.speed_category = speed_category
        self.speed_value = SPEED_MAP[speed_category]
        self.busy_until = busy_until
        self.total_service_time = total_service_time
        self.idle_time = idle_time

# Define class for Event
class Event():
    def __init__(self, time, event_type, customer=None):
        self.time = time
        self.event_type = event_type
        self.customer = customer

# Function to get priority of customer
def get_priority(customer):
    if customer.has_appointment and customer.type == "vip":
        return 1
    if customer.has_appointment and customer.type == "elderly":
        return 2
    if customer.has_appointment and customer.type == "regular":
        return 3
    if not customer.has_appointment and customer.type == "vip":
        return 4
    if not customer.has_appointment and customer.type == "elderly":
        return 5
    return 6  # regular without appointment

def start_service(current_time, customer, teller, event_queue, log):
    # Start service
    start_service_time = current_time
    customer.service_start_time = start_service_time


    # Determine service duration based on teller speed
    match teller.speed_category:
        case "fast":
            service_duration = random.uniform(1, 3)
        case "medium":
            service_duration = random.uniform(3, 5)
        case "slow":
            service_duration = random.uniform(5, 7)

    # Update teller status
    teller.busy_until = start_service_time + service_duration
    teller.total_service_time += service_duration

    # Schedule departure event and log
    heapq.heappush(event_queue, (teller.busy_until, next(counter), Event(teller.busy_until, "departure", customer)))
    log.append(f"Customer {customer.id} starts service with Teller {teller.id} at {start_service_time:.2f} for {service_duration:.2f} seconds")

# Define main simulation function
def BankSimulation(customers, tellers):
    # Initialize data structures
    event_queue = []
    customer_queue = []
    log = []

    # Stats
    served_customers = 0
    left_customers = 0
    total_wait_time = 0

    # Initialize event queue
    for customer in customers:
        heapq.heappush(event_queue, (customer.arrived, next(counter), Event(customer.arrived, "arrival", customer)))
    
    # Process events
    while event_queue:
        current_time, _, event = heapq.heappop(event_queue)

        # Log event
        log.append(f"Time {current_time:.2f}: Event {event.event_type} for Customer {event.customer.id}")

        if event.event_type == "arrival":
            # Check for available tellers
            free_tellers = [t for t in tellers if t.busy_until <= current_time]

            if free_tellers:
                free_tellers.sort(key=lambda t: t.speed_value, reverse=True)
                free_teller = free_tellers[0]
                start_service(current_time, event.customer, free_teller, event_queue, log)
            else:
                priority = get_priority(event.customer)
                heapq.heappush(customer_queue, (priority, current_time, event.customer))
                log.append(f"Customer {event.customer.id} queued at {current_time:.2f} with priority {priority}")

                if event.customer.patience > 0:
                    leave_time = current_time + event.customer.patience
                    heapq.heappush(event_queue, (leave_time, next(counter), Event(leave_time, "leave", event.customer)))

        elif event.event_type == "departure":
            # Service completed, log and update stats
            served_customers += 1
            wait_time = event.customer.service_start_time - event.customer.arrived
            total_wait_time += wait_time
            log.append(f"Customer {event.customer.id} completed service at {current_time:.2f}, waited {wait_time:.2f} seconds")

            # Assign next customer
            if customer_queue:
                priority, _, next_customer = heapq.heappop(customer_queue)
                free_tellers = [t for t in tellers if t.busy_until <= current_time]
                free_tellers.sort(key=lambda t: t.speed_value, reverse=True)
                free_teller = free_tellers[0]
                start_service(current_time, next_customer, free_teller, event_queue, log)
        
        elif event.event_type == "leave":
            # Customer leaves due to impatience
            still_waiting = next((i for i, (_, _, c) in enumerate(customer_queue) if c.id == event.customer.id), None)

            if still_waiting is not None:
                customer_queue.pop(still_waiting)
                heapq.heapify(customer_queue)
                left_customers += 1
                log.append(f"Customer {event.customer.id} left the queue at {current_time:.2f} due to impatience")

    # Final statistics and printing
    average_wait_time = total_wait_time / served_customers if served_customers > 0 else 0

    print(f"\t{"="*15}EVENT LOG{"="*15}\n")
    for line in log:
        print(f"{line}\n")

    print(f"Total Customers served: {served_customers}")
    print(f"Total Customers left: {left_customers}")
    print(f"Average wait time: {average_wait_time:.2f} seconds")
    for t in tellers:
        print(f"Teller {t.id} total service time: {t.total_service_time:.2f} seconds")


# Test data
customers = [
    Customer(1, "regular", 0, patience=3),
    Customer(2, "VIP", 1, patience=1),
    Customer(3, "regular", 3, patience=5),
    Customer(4, "elderly", 4, patience=2, has_appointment=True),
    Customer(5, "VIP", 5, patience=4),
    Customer(6, "regular", 6, patience=3, has_appointment=True)
]

tellers = [
    Teller(1, "fast"),
    Teller(2, "medium"),
    Teller(3, "slow")
]

BankSimulation(customers, tellers)
