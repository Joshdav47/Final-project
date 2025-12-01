import random
import time
import threading


def bankSimulation(customers, tellers, max_wait_allowed=None):
    service_types = ["deposit", "withdraw", "inquiry"]
    queue = []
    sim_start = time.time()
    pending_customers = [
        {"type": t, "arrived": sim_start, "id": i} for i, t in enumerate(customers)
    ]
    last_helped_time = sim_start
    total_idle_accumulated = 0.0
    max_idle = 0.0
    service_count = 0
    total_service_time_by_teller = {"fast": 0.0, "medium": 0.0, "slow": 0.0}
    served_count_by_teller = {"fast": 0, "medium": 0, "slow": 0}
    total_wait_time = 0.0
    max_wait = 0.0
    wait_count = 0
    wait_time_by_type = {"VIP": 0.0, "Elderly": 0.0, "Regular": 0.0}
    wait_count_by_type = {"VIP": 0, "Elderly": 0, "Regular": 0}
    left_count = 0
    if max_wait_allowed is None:
        max_wait_allowed = {"VIP": 2.0, "Elderly": 4.0, "Regular": 8.0}

    lock = threading.Lock()
    cond = threading.Condition(lock)
    busy_count = 0
    threads = []

    def pop_next_customer():
        if queue:
            cust = queue.pop(0)
            return cust, cust["type"]

        for typ in ("VIP", "Elderly", "Regular"):
            for idx, rec in enumerate(pending_customers):
                if rec["type"] == typ:
                    return pending_customers.pop(idx), typ
        return None, None

    def handle_service(teller, customer, service_type, dur):
        nonlocal busy_count, last_helped_time, total_idle_accumulated, max_idle, service_count
        time.sleep(dur)
        finish = time.time()
        with lock:
            total_service_time_by_teller[teller] += dur
            served_count_by_teller[teller] += 1
            service_count += 1
            busy_count -= 1
            last_helped_time = finish
            tellers.append(teller)
            cond.notify_all()

    print("Bank is open for service!")

    while pending_customers or queue:
        with lock:
            now_check = time.time()
            for i in range(len(pending_customers) - 1, -1, -1):
                rec = pending_customers[i]
                allowed = max_wait_allowed.get(rec["type"], max_wait_allowed.get("Regular", 8.0))
                if now_check - rec["arrived"] > allowed:
                    pending_customers.pop(i)
                    left_count += 1
                    print(f"Customer id={rec['id']} ({rec['type']}) left after waiting {now_check - rec['arrived']:.2f}s (max {allowed}s)")
            for i in range(len(queue) - 1, -1, -1):
                rec = queue[i]
                allowed = max_wait_allowed.get(rec["type"], max_wait_allowed.get("Regular", 8.0))
                if now_check - rec["arrived"] > allowed:
                    queue.pop(i)
                    left_count += 1
                    print(f"Queued customer id={rec['id']} ({rec['type']}) left after waiting {now_check - rec['arrived']:.2f}s (max {allowed}s)")
            assigned = False
            while tellers and (pending_customers or queue):
                customer, typ = pop_next_customer()
                if customer is None:
                    break
                now = time.time()
                if busy_count == 0:
                    idle_since_last = max(0.0, now - last_helped_time)
                    total_idle_accumulated += idle_since_last
                    if idle_since_last > max_idle:
                        max_idle = idle_since_last

                wait = now - customer["arrived"]
                total_wait_time += wait
                wait_count += 1
                if wait > max_wait:
                    max_wait = wait
                wait_time_by_type[customer["type"]] += wait
                wait_count_by_type[customer["type"]] += 1

                teller = tellers.pop(0)
                service = random.choice(service_types)
                if teller == "fast":
                    dur = 2 if service == "deposit" else (4 if service == "withdraw" else 6)
                elif teller == "medium":
                    dur = 4 if service == "deposit" else (6 if service == "withdraw" else 8)
                else:
                    dur = 6 if service == "deposit" else (8 if service == "withdraw" else 10)
                print(f"{typ} customer (id={customer['id']}) is being served by {teller} teller for {service}. Waited {wait:.2f}s")
                busy_count += 1
                t = threading.Thread(target=handle_service, args=(teller, customer, service, dur))
                t.start()
                threads.append(t)
                assigned = True

            if not assigned:
                cond.wait(timeout=0.5)

    for t in threads:
        t.join()

    print(f"Total Customers served: {service_count}")
    print(f"Total idle accumulated between services: {total_idle_accumulated:.2f} seconds")
    if service_count > 0:
        print(f"Average idle between services: {total_idle_accumulated/service_count:.2f} seconds")
    print(f"Max idle between services: {max_idle:.2f} seconds")
    print(f"Service time by teller: {total_service_time_by_teller}")
    print(f"Served count by teller: {served_count_by_teller}")
    print(f"Total wait time (all customers): {total_wait_time:.2f} seconds")
    if wait_count > 0:
        print(f"Average wait time: {total_wait_time/wait_count:.2f} seconds")
    print(f"Max wait time: {max_wait:.2f} seconds")
    print(f"Wait time by type: {wait_time_by_type}")
    print(f"Customers who left due to excessive wait: {left_count}")
    return {
        "total_idle": total_idle_accumulated,
        "max_idle": max_idle,
        "service_count": service_count,
        "service_time_by_teller": total_service_time_by_teller,
        "served_count_by_teller": served_count_by_teller,
        "total_wait": total_wait_time,
        "max_wait": max_wait,
        "wait_count": wait_count,
        "wait_time_by_type": wait_time_by_type,
        "customers_left": left_count,
    }

def main():
    k = int(random.random() * 10) + 1
    customers = random.choices(["VIP", "Elderly", "Regular"], k=k)
    print(customers)
    tellers = ["fast", "medium", "slow"]
    bankSimulation(customers, tellers)

if __name__ == "__main__":
    main()