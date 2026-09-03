import threading
import queue
import time

task= queue.Queue()
def process_ticket(ticket_id: int):
    print(f"Processing ticket {ticket_id}")
    time.sleep(3)
    print(f"Ticket {ticket_id}")
    

start=time.time()
threads = []
for i in range(1, 6):
    i=task.put(i)
    t = threading.Thread(target=process_ticket, args=(i,))
    threads.append(t)
    t.start()

task.join()

end = time.time()
print(f"{end - start:.2f}")


#implemeting queueing

task= queue.Queue()
