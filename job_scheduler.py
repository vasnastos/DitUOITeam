import schedule,time

def job():
    print("Schedule job to be executed from schedule module")

if __name__=='__main__':
    schedule.every(10).seconds.do(job)
    while True:
        current=time.time()
        schedule.run_pending()
        time.sleep(15)
        print(f'Job executed:{time.time()-current}\'s')