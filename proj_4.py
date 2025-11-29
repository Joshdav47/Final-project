import random
import time

#TODO: Track how much time it takes to serve each customer for each teller type and track how many they served and 
#return average time and total helped

def bankSimulation(customers, tellers):
    service = ["deposit", "withdraw", "inquiry"] # Fast: 2 sec, 4 sec, 6 sec | Medium: 4 sec, 6 sec, 8 sec | Slow: 6 sec, 8 sec, 10 sec
    queue = []
    available_tellers = tellers.copy()
    print("Bank is open for service!")

    for customer in customers:
        while "VIP" in customer:
            if available_tellers and "fast" in available_tellers:
                available_tellers.remove("fast")
                service = random.choice(service)
                print(f"VIP customer is being served by fast teller for {service}.")
                if service == "deposit":
                    time.sleep(2)
                elif service == "withdraw":
                    time.sleep(4)
                else:
                    time.sleep(6)
                available_tellers.append("fast")
            elif available_tellers and "medium" in available_tellers:
                available_tellers.remove("medium")
                service = random.choice(service)
                print(f"VIP customer is being served by medium teller for {service}.")
                if service == "deposit":
                    time.sleep(4)
                elif service == "withdraw":
                    time.sleep(6)
                else:
                    time.sleep(8)
                available_tellers.append("medium")
            elif available_tellers and "slow" in available_tellers:
                available_tellers.remove("slow")
                service = random.choice(service)
                print(f"VIP customer is being served by slow teller for {service}.")
                if service == "deposit":
                    time.sleep(6)
                elif service == "withdraw":
                    time.sleep(8)
                else:
                    time.sleep(10)
                available_tellers.append("slow")
            else:
                print("No tellers available for VIP customer, waiting...")
                queue.append("VIP")

def main():
    k = int(random.random() * 10) + 1
    customers = random.choices(["VIP", "Elderly", "Regular"], k=k)
    print(customers)
    tellers = ["fast", "medium", "slow"]
    bankSimulation(customers, tellers)


if __name__ == "__main__":
    main()