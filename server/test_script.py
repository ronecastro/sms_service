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

# listOfRunningServices()

def test():
    data = [('rone.castro', '+5519997397443', 'rone.castro@lnls.br'), 'WARNING!\n\rSI-13C4:DI-DCCT:Current-Mon < 100\n\rLast Value = 64.431416749\n\r']

    owner = data[0][0]
    phone = data[0][1]
    msg = data[1]

    print('owner:', owner)
    print('phone:', phone)
    print('msg:', msg)

# test()

print('pv = ' + str("%2g" % 0.00000000011 + '\n\r'))