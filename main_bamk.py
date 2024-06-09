import schedule, time

from index import index

# Schedule the task to run every 5 to 10 seconds
schedule.every(5).to(10).seconds.do(index)

# Run the scheduled tasks indefinitely
while True:
   schedule.run_pending()
   time.sleep(1)