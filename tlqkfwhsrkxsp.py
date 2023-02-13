import schedule
import threading
import time     # fps 계산 시 사용


def message():
    print("ddd")
    t = threading.Timer(2, message)
    t.start()

count = 0
message()
while (True):
    print("gdgd")
    time.sleep(1)
    count = count +1
    if count >= 5:
        message().cancel()
        break


#schedule.cancel_job(job1)

