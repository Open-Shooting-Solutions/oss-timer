from apscheduler.schedulers.background import BackgroundScheduler
import time


# Function to be triggered
def my_event(event_name):
    print(f"Event triggered: {event_name}, time: {time.time()}")


# Create a scheduler
scheduler = BackgroundScheduler()

# Schedule multiple events
scheduler.add_job(my_event, "interval", seconds=5, args=["Event 1"], id="event1")
scheduler.add_job(my_event, "interval", seconds=10, args=["Event 2"], id="event2")
scheduler.add_job(my_event, "interval", seconds=15, args=["Event 3"], id="event3")

# Start the scheduler
scheduler.start()

# Let it run for a while
time.sleep(7)

# Pause events (by pausing the scheduler)
print("Pausing...")
scheduler.pause()

# Wait for a few seconds before resuming
time.sleep(5)

# Resume events
print("Resuming...")
scheduler.resume()

# Let it run a bit more to show resumption
time.sleep(10)

# Shut down the scheduler gracefully
scheduler.shutdown()
