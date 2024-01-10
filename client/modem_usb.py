import serial, time, re, psutil

##############################################################
# We need to change permission for the usb file of the modem #
# To make a udev file adding a specific rule for this modem, #
# two parameter are necessary: idVendor and idProduct, found #
# with command: <lsusb -vvv> (look for ZTE modem in the list)#
# Udev file goes to: /etc/udev/rules.d/<50-filename.rules> ###
# Add the bellow line to the file: ###########################
# SUBSYSTEMS=="usb", ATTRS{idVendor}=="<idVendor_for_modem>", ATTRS{idProduct}=="<idProduct_for_modem>", GROUP="users", MODE="0666"
# In optiplex-7070-sc-2, idVendor=19d2 and idProduct=1589 ####
# Reload udev with command: <sudo udevadm control --reload> ##
# Insert (or take out and reinsert) modem in the usb slot ####
# Verify modem file permission with the bellow command: ######
# <stat /dev/ttyUSB0> ########################################
# Access must be with description (0666/crw-rw-rw) ###########
# Also, kill ModemManagement proccess with commands: #########
# <sudo lsof -t /dev/ttyUSB0> then <sudo kill proccess_id> ###
# Sometimes it's necessary kill, start, than kill again the ##
# ModemManager proccess. Use the following commands: #########
# <sudo service ModemManager status> (look for Main PID) #####
# <sudo kill process_ID> #####################################
# <sudo service ModemManager start> ##########################
# Keep ModemManager proccess killed! #########################
# Wait until the modem is ready, sometimes 60 seconds ########
##############################################################


class Modem:
    def __init__(self, path='/dev/ttyUSB0', debug=False):
        self.path = path
        self.debug = debug
        self.msgnumber = None
        self.serial_connection = serial.Serial(path, baudrate=115200, timeout=5)
        self.serial_connection.reset_input_buffer()

    def send_to_modem(self, msg, sleep=0.2):
        self.serial_connection.write(msg.encode())
        time.sleep(sleep)

    def get_answer(self, strt_sleep=0.2, sleep=0.2):
        time.sleep(strt_sleep)
        quantity = self.serial_connection.in_waiting
        ans = ''
        while True:
            if quantity > 0:
                ans += self.serial_connection.read(quantity).decode()
                # print('ans get answer: ', ans)
                time.sleep(sleep)
            else:
                time.sleep(sleep)
            # print('quantity before:', quantity)
            quantity = self.serial_connection.in_waiting
            # print('quantity after:', quantity)
            if quantity == 0:
                break
        if self.debug:
            print(ans)
        return ans

    def echo_mode(self, mode=1):
        if mode == 0:
            cmd = 'ATE0' + '\r'
        elif mode == 1:
            cmd = 'ATE1' + '\r'
        self.send_to_modem(cmd)
        ans = self.get_answer(sleep=0.2)
        return ans

    def send_command(self, cmd, sleep=2, endchar='\r'):
        if endchar == 'ESC':
            endchar = chr(26)
        aux = cmd + endchar
        self.send_to_modem(aux)
        return self.get_answer(int(sleep))

    def reset(self):
        cmd = 'ATZ' + '\r'
        self.send_to_modem(cmd)
        ans = self.get_answer(sleep=2)
        return ans

    def verbose_on_error(self, turn=True):
        if turn:
            cmd = 'AT+CMEE=1' + '\r'
            self.send_to_modem(cmd)
            ans = self.get_answer(sleep=0.2)
        elif turn == False:
            cmd = 'AT+CMEE=0' + '\r'
            self.send_to_modem(cmd)
            ans = self.get_answer(sleep=0.2)
        return ans

    def set_mode(self, mode='text'):
        if mode == 'text':
            cmd = 'AT+CMGF=1' + '\r'
            self.send_to_modem(cmd)
            ans = self.get_answer(sleep=0.5)
            return ans
        elif mode == 'PDU':
            return 'error on set_mode: PDU mode not implemented'
        else:
            return 'error on set_mode: option not supported'

    def write_to_storage(self, index, msg):
        cmd = 'AT+CMGW=' + '"' + index + '"' + '\r'
        self.send_to_modem(cmd)
        ans = self.get_answer(sleep=0.2)
        if ans == '>':
            cmd = msg + chr(26)
            self.send_to_modem(cmd)
            ans = self.get_answer(sleep=0.2)
            if '+CMGW:' in ans:
                pattern = '[\d]+'
                if re.search(pattern, ans) is not None:
                    for catch in re.finditer(pattern, ans):
                        msgnumber = catch[0]
                    return msgnumber
        return ans

    def send_from_storage(self, index):
        cmd = 'AT+CMSS=' + str(index) + '\r'
        self.send_to_modem(cmd)
        ans = self.get_answer(sleep=0.2)
        return ans

    def set_storage_area(self, area='ME'):
        if area == 'ME':
            area = '"' + area + '"'
            cmd = 'AT+CPMS=' + area + ','+ area + '\r'
            self.send_to_modem(cmd)
            ans = self.get_answer(sleep=0.2)
            return ans

    #index = memory location of stored SMS, set storage area before using this.
    #flags:
    #0 = delete only selected message;
    #1 = ignore index (use any number), delete all received read;
    #2 = ignore index, delete all received read and stored sent;
    #3 = ignore index, delete all received read, stored unsent and stored sent;
    #4 = ignore index, delete all stored SMS messages;
    def clear_storage(self, index, flag=4):
        aux = str(index) + ',' + str(flag) + '\r'
        cmd = 'AT+CMGD=' + aux
        self.send_to_modem(cmd)
        ans = self.get_answer(sleep=1)
        return ans

    def kill_modem_proc(self):
        for proc in psutil.process_iter():
            if proc.name() == 'ModemManager':
                proc.kill()
                print('Modem process killed')

    def initialize(self):
        self.reset()
        ans = self.reset()
        if self.debug == True:
            if ('OK' in ans) and ('nOK' not in ans):
                self.verbose_on_error()
            else:
                return ans
        if ('OK' in ans) and ('nOK' not in ans):
            self.set_mode(mode='text')
        else:
            return ans
        if ('OK' in ans) and ('nOK' not in ans):
            self.set_storage_area(area='ME')
        else:
            return ans
        if ('OK' in ans) and ('nOK' not in ans):
            return ans
        else:
            return ans

    #Operations Group number
    def sendsms(self, mode='direct', number='+5519997397443', msg='SMS message test.', clearmemo=True):
        if mode == 'direct':
            cmd = 'AT+CMGS=' + '"' + number + '"' + '\r'
            self.send_to_modem(cmd)
            ans = self.get_answer(sleep=0.2)
            if '>' in ans:
                cmd = msg + chr(26)
                self.send_to_modem(cmd)
                time.sleep(5)
                ans = self.get_answer()
            if msg and 'OK' in ans:
                return 'ok'
            else:
                return 'nOk'

        elif mode == 'indirect':
            cmd = 'AT+CMGW=' + '"' + number + '"' + '\r'
            self.send_to_modem(cmd)
            ans = self.get_answer(sleep=0.2)
            if '>' in ans:
                cmd = msg + chr(26)
                self.send_to_modem(cmd)
                ans = self.get_answer(sleep=0.2)
                if '+CMGW:' in ans:
                    pattern = '[\d]+'
                    if re.search(pattern, ans) is not None:
                        for catch in re.finditer(pattern, ans):
                            msgnumber = catch[0]
                        if msgnumber.isnumeric():
                            cmd = 'AT+CMSS=' + msgnumber + '\r'
                            self.send_to_modem(cmd)
                            ans = self.get_answer(sleep=4)
                            if ('OK' in ans) and ('nOK' not in ans):
                                if clearmemo:
                                    self.clear_storage(msgnumber)
                                    return ans
                            return ans
                return ans
            return ans

    def closeconnection(self):
        self.serial_connection.close()

# m = Modem(debug=True)
# m.initialize()
# m.sendsms(mode='direct')
# m.closeconnection()
