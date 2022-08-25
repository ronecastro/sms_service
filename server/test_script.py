import os

def listOfRunningServices():
    try:        
        print("Listing all running service")
        #Check all the running service
        for line in os.popen("systemctl --type=service --state=running"):
            services = line.split()
            print(services)
            pass
        
    except OSError as ose:
        print("Error while running the command", ose)
   
    pass

listOfRunningServices()

