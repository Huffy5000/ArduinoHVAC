# Milestone 2 Code Group C18
# Updated 15/09/2023




import matplotlib.pyplot as plt
import numpy as np
import time 
import random
import math
from pymata4 import pymata4

#Define variables
correctPin = 8888
goalTemp = 20 
allowableTempRange = 0.5

pollingRate = 2
srPins = [7,8,9]
digit = [3,4,5,6]
indoorFilteredTempList = []
outdoorFilteredTempList=[]

board=pymata4.Pymata4()
heatCool = None
lockedOut = False
lockeoutStartTime = 2


################################################ SEVEN SEGMENT FUNCTION #############################################

def shift_register_seq(board, pins, sequence):
    serPin = pins[0]
    shiftRegClock = pins[2]
    regLatch = pins[1]
    board.digital_pin_write(serPin,0)
    for i in range(len(sequence)):
        board.digital_pin_write(shiftRegClock,1)
        board.digital_pin_write(shiftRegClock,0)
    sequence = sequence[::-1]
    for num in sequence:
        board.digital_pin_write(pins[0],int(num))
        board.digital_pin_write(shiftRegClock,1)
        board.digital_pin_write(shiftRegClock,0)
    board.digital_pin_write(regLatch,1)
    board.digital_pin_write(regLatch,0)

def display_text(board,srPins,digit,display):
    # display_text will print given text to the seven segment display as long as under or equal to 4 characters for given runtime
    # INPUTS:
    # board: arduino object
    # srPins: list of pins that control the shift register
    # digit: list of pins that activate each digit
    # display: str to display on the seven seg display
    # OUTPUTS:
    # None

    #dictionary contains info on which segment should be turned on for the letter, 1 is on and 0 is off
    lookupDictionary = {
    "0":"1111110",
    "1":"0110000",
    "2":"1101101",
    "3":"1111001",
    "4":"0110011",
    "5":"1011011",
    "6":"1011111",
    "7":"1110000",
    "8":"1111111",
    "9":"1111011",
    "A":"1110111",
    "B":"0011111",
    "C":"1001111",
    "D":"0111101",
    "E":"1001111",
    "F":"1000111",
    "G":"1011110",
    "H":"0010111",
    "I":"0110000",
    "J":"0111100",
    "K":"1010111",
    "L":"0001110",
    "M":"1010101",
    "N":"0010101",
    "O":"0011101",
    "P":"1100111",
    "Q":"1110011",
    "R":"0000101",
    "S":"1011011",
    "T":"0001111",
    "U":"0011100",
    "V":"0101010",
    "W":"1101011",
    "X":"0110111",
    "Y":"0111011",
    "Z":"1101100",
    " ":"0000000"}

    # initiliaze by setting the pins needed to output
    for pin in srPins:
        board.set_pin_mode_digital_output(pin)
        #will iterate through each character of text
    for elem in range(len(display)):
        board.set_pin_mode_digital_output(digit[elem])
        pinSeq = lookupDictionary[display[elem].upper()]+"00000000"
        shift_register_seq(board,srPins,pinSeq)
        # writing 0 to digit turns digit on
        board.digital_write(digit[elem],0)
        # will flash it briefly to move on to next character
        board.digital_write(digit[elem],1)

def scroll_text(board,srPins, digit,fullText):
    # scroll_text will print text to seven segment display, but if text is longer than 4 digits it'll scroll
    # INPUTS
    # board: 
    start = time.time()
    if len(fullText)<=4:
        while time.time()-start<5:
            display_text(board,srPins,digit,fullText)
    else:
        scrollText = fullText+" "
        start = 0
        while start+4<=len(scrollText):
            if start+4==len(scrollText):
                scrollText+=scrollText
            scrollStart = time.time()
            croppedText = scrollText[start:start+4]
            while time.time()-scrollStart<0.1:
                display_text(board,srPins,digit,croppedText)
            start+=1

                    
### Output Subsystem Functions
#Fan Speed
def fan_LED_status(filteredTemperature, goalTemp, allowableTempRange,outdoorFilteredTemp):
    """
    fenLEDStatus function will turn on relevant LEDs according to given parameters
    INPUTS:
    filteredTemperature: the temperature reading in celsius degrees.
    goalTemp: the desired temperature in degrees celsius.
    allowableTempRange: the acceptable range around goalTemp that is allowed.
    OUTPUTS:
    str output of fan status.
    """

    global heatCool

    if filteredTemperature < goalTemp - allowableTempRange:
        heatCool = "Heat"


        ##This is a climate control decision
        if outdoorFilteredTemp-goalTemp>10:
            #Heat at low speed if really hot outside but cold inside house 
            board.set_pin_mode_digital_output(16) 
            board.digital_write(16,1)
            return "Fan is heating at low speed"



        elif filteredTemperature<goalTemp-allowableTempRange-4:
            #Turn Both RED LED's On
            pins = [16,17]
            for pin in pins:
             board.set_pin_mode_digital_output(pin)
             board.digital_write(pin,1)
             return "Fan is heating at high speed"
            

        elif filteredTemperature<goalTemp-allowableTempRange:
             #Turn one RED LED's On
            board.set_pin_mode_digital_output(16)
            board.digital_write(16,1)
            board.set_pin_mode_digital_output(17)
            board.digital_write(17,0)
            return "Fan is heating at low speed"
        
        

        


    elif filteredTemperature > goalTemp + allowableTempRange:
        heatCool = "Cool"


        ##This is a climate control decision
        if goalTemp-outdoorFilteredTemp>10:
            #If hot inside the house
            # We want to cool
            #If really cold outsie
            # cool slowly 
            board.set_pin_mode_digital_output(18)
            board.digital_write(18,1)
            return "Fan is cooling at low speed"
        
        elif filteredTemperature>goalTemp+allowableTempRange+4:
            #Turn Both BLUE LED's On
            pins = [18,11]
            for pin in pins:
             board.set_pin_mode_digital_output(pin)
             board.digital_write(pin,1)
            return "Fan is cooling at high speed"
        

        elif filteredTemperature>goalTemp+allowableTempRange:
             #Turn one BLUE LED's On
            board.set_pin_mode_digital_output(18)
            board.digital_write(18,1)
            board.set_pin_mode_digital_output(11)
            board.digital_write(11,0)
            return "Fan is cooling at low speed"
        
    elif (goalTemp - allowableTempRange) <= filteredTemperature <= (goalTemp + allowableTempRange):
        board.digital_write(16,0)
        board.digital_write(17,0)
        board.digital_write(18,0)
        board.digital_write(11,0)
         
        return "Temperature is within acceptable range"



#################################### DATA OBSERVATION #####################################



def generate_graph(indoorFilteredTempList,graphModeChoice,outdoorFilteredTempList):
    """
    # generate_graph function will create a graph of the temp readings over the last 20 seconds on the x axis.
    # INPUTS: 
    # filteredTempList: list of filtered temperature readings.
    # OUTPUTS:
    # No returns, will generate graph.
    """
    try:
            if graphModeChoice==1:
                fig = plt.figure()
                ax = fig.add_subplot(1,1,1)
                #Define x and y axis values  
                xTime = np.linspace(20,0,10)
                yVals = indoorFilteredTempList[-10:]
                #Clear all graph and plot
                ax.clear()
                ax.plot(xTime,yVals)
                ax.invert_xaxis()
                #Adjust plot formatting 
                plt.title("Room temperature over last 20 seconds")
                plt.ylabel("Room temperature (C)")
                plt.xlabel("Time (s)")
                
                currentTime = time.localtime(time.time())
                currentDay = currentTime.tm_mday
                currentMonth = currentTime.tm_mon
                currentYear = currentTime.tm_year
                currentHour = currentTime.tm_hour
                currentMinute = currentTime.tm_min
                currentSec = currentTime.tm_sec
                ########################################ERROR WITH THIS FILEPATH HAS TO ADJUST TO ALL OF EM
                dateTimeString = "IndoorTemp_"+str(currentDay)+"_"+str(currentMonth)+"_"+str(currentYear)+"."+str(currentHour)+"."+str(currentMinute)+"."+str(currentSec)
                plt.savefig("C:\\Users\\dhruv\\Documents\\TestGraphs\\" + str(dateTimeString)+".png")
                plt.show()
                

            elif graphModeChoice ==2:
                fig = plt.figure()
                ax=fig.add_subplot(1,1,1)
                #Define x and y values 
                xTime=np.linspace(20,0,10)
                yVals = outdoorFilteredTempList[-10:]
                #Clear graph and plot
                ax.clear()
                ax.plot(xTime,yVals)
                ax.invert_xaxis()
                #AdjustFormatting
                plt.title("Outdoor temperature over last 20 seconds")
                plt.ylabel("Outdoor temperature (C)")
                plt.xlabel("Time (s)")

                currentTime = time.localtime(time.time())
                currentDay = currentTime.tm_mday
                currentMonth = currentTime.tm_mon
                currentYear = currentTime.tm_year
                currentHour = currentTime.tm_hour
                currentMinute = currentTime.tm_min
                currentSec = currentTime.tm_sec


                ########################################ERROR WITH THIS FILEPATH HAS TO ADJUST TO ALL OF EM
                dateTimeString = "OutdoorTemp_"+str(currentDay)+"_"+str(currentMonth)+"_"+str(currentYear)+"."+str(currentHour)+"."+str(currentMinute)+"."+str(currentSec)
                plt.savefig("C:\\Users\\dhruv\\Documents\\TestGraphs\\" + str(dateTimeString)+".png")
                plt.show()
                
                plt.show()
               


            elif graphModeChoice==3:
                fig = plt.figure()
                ax=fig.add_subplot(1,1,1)
                #Define x and y vectors
                xTime = np.linspace(22,2,11)
                #Create rate of change list from indoor temperature
                rateOfChangeList =[]
                for i in range(len(indoorFilteredTempList)-1):
                    rateOfChange = (indoorFilteredTempList[i+1]-indoorFilteredTempList[i])/(xTime[i]-xTime[i+1])
                    rateOfChangeList.append(rateOfChange)

                #Clear graph and plot
                ax.clear()
                ax.plot(xTime[-9:],rateOfChangeList)
                ax.invert_xaxis()
                
                #AdjustFormatting
                plt.title("Indoor Temperature rate of change over 20 seconds")
                plt.ylabel("Indoor Temperature Rate of Change (dT/dt)")
                plt.xlabel("Time (s)")

                currentTime = time.localtime(time.time())
                currentDay = currentTime.tm_mday
                currentMonth = currentTime.tm_mon
                currentYear = currentTime.tm_year
                currentHour = currentTime.tm_hour
                currentMinute = currentTime.tm_min
                currentSec = currentTime.tm_sec

                ########################################ERROR WITH THIS FILEPATH HAS TO ADJUST TO ALL OF EM
                dateTimeString = "RateOfChangeIndoorTemp_"+str(currentDay)+"_"+str(currentMonth)+"_"+str(currentYear)+"."+str(currentHour)+"."+str(currentMinute)+"."+str(currentSec)
                plt.savefig("C:\\Users\\dhruv\\Documents\\TestGraphs\\" + str(dateTimeString)+".png")
                plt.show()
                
                plt.show()
                
                
               
               
    except KeyboardInterrupt:
        plt.close()
        data_observation_mode(indoorFilteredTempList,2,outdoorFilteredTempList)

              





def data_observation_mode(indoorFilteredTempList,pollingRate,outdoorFilteredTempList):
    """
    data_observation_mode function will enter the data observation mode and generate graph 
    INPUTS:
    filteredTempList: list of filtered temperature readings.
    pollingRate: time taken for one polling cycle in seconds
    OUTPUTS:
    No returns
    """

    try:
          if len(indoorFilteredTempList)<10:
            dataTime = pollingRate*(10-len(indoorFilteredTempList))
            print(f"Insufficient data, please wait {dataTime} seconds before retrying")
            raise KeyboardInterrupt
          elif len(indoorFilteredTempList)>=10:
              
            while True:
                    try:
                        print("\n====================GRAPH SELECTION====================")
                        graphModeChoice = int(input("Select graph:\n(1) Indoor Temperature\n(2) Outdoor Temperature\n(3) Indoor Temperature rate of change\n"))
                        global heatCool
                        if graphModeChoice == 1:
                            generate_graph(indoorFilteredTempList=indoorFilteredTempList,graphModeChoice=graphModeChoice,outdoorFilteredTempList=outdoorFilteredTempList)
                            while True:
                                    try:
                                        scroll_text(board,srPins,digit,heatCool)
                                    except KeyboardInterrupt:
                                        break
                            raise KeyboardInterrupt
                          
                        elif graphModeChoice == 2:    
                            generate_graph(indoorFilteredTempList=indoorFilteredTempList,graphModeChoice=graphModeChoice,outdoorFilteredTempList=outdoorFilteredTempList)
                            while True:
                                    try:
                                        scroll_text(board,srPins,digit,heatCool)
                                    except KeyboardInterrupt:
                                        break
                            raise KeyboardInterrupt
                           
                        elif graphModeChoice == 3:
                            generate_graph(indoorFilteredTempList=indoorFilteredTempList,graphModeChoice=graphModeChoice,outdoorFilteredTempList=outdoorFilteredTempList)
                            while True:
                                    try:
                                        scroll_text(board,srPins,digit,heatCool)
                                    except KeyboardInterrupt:
                                        break

                            raise KeyboardInterrupt
                        else:
                            raise ValueError           
                        
                    except ValueError:
                        print("Invalid input. Select form given graph choices.")
                        data_observation_mode(indoorFilteredTempList,pollingRate,outdoorFilteredTempList)     
                    except KeyboardInterrupt:
                        plt.close()
                        select_operating_mode()
              
    except KeyboardInterrupt:
        plt.close()
        select_operating_mode()
               


#################################### MAINTAINENCE ADJUSTMENT #####################################
def maintainence_adjustment_mode(correctPIN):
    """
    maintainence_adjustment_mode function will allow paramaters to be adjusted
    INPUTS:
    correctPIN: the pin required as an int to enter maintainence_adjustment_mode
    OUTPUTS:
    no returns, will change global variables.
    """
    global lockedOut,lockeoutStartTime


    try: 
        #3 attempts given to get correct PIN
        if lockedOut == True:
            if time.time()-lockeoutStartTime >=120:
                lockedOut = False

        if lockedOut==True:
            print(f"Too many incorrect attempts, user is locked out for {120-(time.time()-lockeoutStartTime)} seconds ")
            raise KeyboardInterrupt
        attempts = 3
        while attempts!=0:
            userPIN = int(input("Enter 4 Digit PIN to access Maintenance Adjustment Mode: "))
            if userPIN!=correctPIN:
                attempts-=1
                print("Incorrect PIN")
                #if all attempts are exhausted maintenance mode will be locked and return to selection menu
                if attempts ==0:
                    lockedOut =True
                    lockeoutStartTime=time.time()
                    print("Too many incorrect attempts, user has been locked out for 2 minutes")
                    select_operating_mode() #Back to home screen
            #will exit loop when correct PIN is given
            else:
                break
        #makes all changes made by user global
        global goalTemp, allowableTempRange
        #will continue asking for new parameters until ctrl+c is selected
        while True:
            
            #current parameters
            print(f"1) Goal Temperature: {goalTemp} Degrees\n2) Allowable Temperature Range: {allowableTempRange} Degrees")
            #runs until valid paramater is selected
            

            while True:    
                try:
                    userPick = int(input("Pick a parameter to change: "))
                    if userPick ==1 or userPick==2:
                        break
                    print("Please input valid number")
                except TypeError:
                    print("Please input valid number")
                except KeyboardInterrupt:
                    select_operating_mode()

            #validate goalTemp must be a valid float element
            if userPick==1:
                try:
                    timeoutTimer = time.time()
                    userGoalTemp = float(input("Set new Goal Temperature: "))
                    timeoutTimerEnd = time.time()
                    if timeoutTimerEnd-timeoutTimer>=30:
                        print("You have been timed out")
                        raise KeyboardInterrupt
                    if userGoalTemp>60 or userGoalTemp<0:
                        raise TypeError
                    goalTemp = userGoalTemp
                except TypeError:
                    print("Invalid Change. Goal Temperature must be a float between 0 and 60 degrees C")
                except KeyboardInterrupt:
                    select_operating_mode()
                
        
            
               
            #validate temp range allowed is a valid float element
            elif userPick==2: 
                try:
                    timeoutTimer = time.time()
                    userTempRange = float(input("Set new Allowable Temperature Range: "))
                    timeoutTimerEnd = time.time()

                    if timeoutTimerEnd-timeoutTimer>=30:
                        print("You have been timed out")
                        raise KeyboardInterrupt
                    
                    if userTempRange>10 or userTempRange<0:
                        raise TypeError
                    allowableTempRange = userTempRange
                except TypeError:
                    print("Invalid Change. Temperature range must be number and less than 10 and greater than 0 degrees")
                except KeyboardInterrupt:
                    select_operating_mode()
    #at any given time if ctrl+c is pressed, maintenance mode is exited. 
    except KeyboardInterrupt:
        select_operating_mode()


#################################### Thermister Function #########################################

def thermistor_inside():
    """ 
    thermistor function will take resistance measurements from thermistor and converted to temp reading
    INPUTS:
    None
    OUTPUTS:
    temperature: calculated temperature reading.
    """

    board.set_pin_mode_analog_input(0)
    resistance_1 = 10000
    voltageIn = 5

    while True:
        #Reading analog value from circuit
        analogValue = board.analog_read(0)

        #Checking if analog value has returned a valid output
        if analogValue[0] != 0:
            #Calculating the voltage from analog value
            voltageOut = (analogValue[0]/1023)*5
            #Calcuating the resistance of thermistor from voltage divider equation
            resistance_2 = (voltageOut*resistance_1)/(voltageIn-voltageOut)
            #Calcuating temperature from calibrated trend line
            temperature = -23.211*math.log(resistance_2)+240.39

            if temperature<-10 or temperature>60:
                thermistor_inside()
            
            global indoorFilteredTempList
            if len(indoorFilteredTempList)!=0:
                if temperature> indoorFilteredTempList[-1] + 10 or temperature < indoorFilteredTempList[-1]-10:    
                    thermistor_inside()
                
                if temperature> indoorFilteredTempList[-1] + 2 or temperature < indoorFilteredTempList[-1]-2:
                    if temperature>indoorFilteredTempList[-1]+2:
                        rateOfChange=(temperature-indoorFilteredTempList[-1])/2
                        print(f"Warning! Temperature is rapidly increasing at {rateOfChange} degrees/second")
                        board.set_pin_mode_digital_output(2)
                        board.digital_write(2,1)
                        #Buzzer sound

                    elif temperature<indoorFilteredTempList[-1]-2:
                        rateOfChange=(temperature-indoorFilteredTempList[-1])/2
                        print(f"Warning! Temperature is rapidly decreasing at {rateOfChange} degrees/second")
                        board.set_pin_mode_digital_output(12)
                        board.digital_write(12,1)
                    for i in range(5):
                        pin = 10
                        board.set_pin_mode_digital_output(pin)
                         
                        board.digital_pin_write(pin,1)
                        time.sleep(0.5)
                        board.digital_pin_write(pin,0)  #THIS IS BLINKING YELLOW LED
                        time.sleep(0.5)

                    thermistor_inside()
            board.digital_pin_write(12,0)
            board.digital_pin_write(2,0)      
            return temperature
        
def thermistor_outside():
    """ 
    thermistor outside function will take resistance measurements from outside thermistor and converted to temp reading
    INPUTS:
    None
    OUTPUTS:
    temperature: calculated temperature reading.
    """
    


    #Setting pin and defining resistances and voltages of the circuit 
    board.set_pin_mode_analog_input(1)
    resistance_1 = 10000
    voltageIn = 5

    while True:
        #Reading analog value from circuit
        analogValue = board.analog_read(1)
        #Checking if analog value has returned a valid output
        if analogValue[0] != 0:
            #Calculating the voltage from analog value
            voltageOutsideThermistor = (analogValue[0]/1023)*5
            #Calcuating the resistance of thermistor from voltage divider equation
            resistance_2_outside = (voltageOutsideThermistor*resistance_1)/(voltageIn-voltageOutsideThermistor)
            #Calcuating temperature from calibrated trend line
            temperatureOutside = -32.4275*math.log(resistance_2_outside)+324.805
            
            
           

            #Call list of previous outside temperature values if they exist
            global outdoorFilteredTempList
            if len(outdoorFilteredTempList)!=0:
                #If current temperature value is 5 degrees different from previous value disregard current temperature value and call funciton
                if temperatureOutside> outdoorFilteredTempList[-1] + 5 or temperatureOutside < outdoorFilteredTempList[-1]-5:
                    thermistor_outside()
            #If temperature is within appropriate ranges, return outside temperature value
            return temperatureOutside




#################################### LDR FUNCTION ##############################################

def calculate_LDR_resistance(pin):
        r1Resistance=2000
        board.set_pin_mode_analog_input(pin)
        readingList = board.analog_read(pin)
         
        voltageReading = readingList[0]
              
        voltageLDR = (voltageReading/1023)*5

        resistanceLDR = (voltageLDR*r1Resistance)/(1+voltageLDR)

        return resistanceLDR

    
def validate_LDR_resistance(pin):
         
        resistanceLDR = calculate_LDR_resistance(pin)

        if resistanceLDR<0:
           validate_LDR_resistance(pin)
            
            
        

        if resistanceLDR<700:
            time.sleep(0.5)
            newResistanceLDR = calculate_LDR_resistance(pin)
            if newResistanceLDR<700:
                print("Possible Fire. Board is shutting down")
                board.shutdown()
                time.sleep(2)
            else:
                return newResistanceLDR
            
        return resistanceLDR

        
        
        

#################################### LED THERMOMETER FUNCTION ##################################
def thermometer():
        
    # Set up pins
    serial = 2
    clock = 3
    latch = 4


    board.set_pin_mode_digital_output(latch)
    board.set_pin_mode_digital_output(serial)
    board.set_pin_mode_digital_output(clock)

    # Write to board
    board.digital_write(latch,0)
    global indoorFilteredTempList


    if indoorFilteredTempList[-1] <= 12: # Very cold - 1 BLUE
        for c in range(8):
            pin1 = "0000000100000000"
            board.digital_write(serial,int(pin1[c]))
            board.digital_write(clock,1)
            board.digital_write(clock,0)

    elif 12 < indoorFilteredTempList[-1] <= 17: # Cold - 2 BLUE
        for d in range(8):
            pin2 = "0000001100000000"
            board.digital_write(serial,int(pin2[d]))
            board.digital_write(clock,1)
            board.digital_write(clock,0)

    elif 17 < indoorFilteredTempList[-1] <= 22: # Cool - 3 BLUE
        for e in range(8):
            pin3 = "0000011100000000"
            board.digital_write(serial,int(pin3[e]))
            board.digital_write(clock,1)
            board.digital_write(clock,0)

    elif 22 < indoorFilteredTempList[-1] <= 27: # Desired temp lower - 1 GREEN
        for g in range(8):    
            pin4 = "0000111100000000"             
            board.digital_write(serial,int(pin4[g]))
            board.digital_write(clock,1)
            board.digital_write(clock,0)

    elif 27 < indoorFilteredTempList[-1] <= 32: # Desired temp upper - 2 GREEN
        for h in range(8):
            pin5 = "0001111100000000"
            board.digital_write(serial,int(pin5[h]))
            board.digital_write(clock,1)
            board.digital_write(clock,0)
        
    elif 32 < indoorFilteredTempList[-1] <= 37: # Warm - 1 RED
        for j in range(8):
            pin6 = "0011111100000000"
            board.digital_write(serial,int(pin6[j]))
            board.digital_write(clock,1)
            board.digital_write(clock,0)

    elif 37 < indoorFilteredTempList[-1] <= 42: # Hot - 2 RED
        for k in range(8):
            pin7 = "0111111100000000"
            board.digital_write(serial,int(pin7[k]))
            board.digital_write(clock,1)
            board.digital_write(clock,0)

    elif 42 < indoorFilteredTempList[-1]:  # Very hot - 3 RED
        for m in range(8):
            pin8 = "1111111100000000"
            board.digital_write(serial,int(pin8[m]))
            board.digital_write(clock,1)
            board.digital_write(clock,0)
        pass

        board.digital_write(latch,1)
        board.digital_write(latch,0)
    

#################################### Normal Operation Mode #####################################
def norm_operating_mode(pollingRate):
    """
    norm_operating_mode function will enter the normal operation mode
    INPUTS:
    pollingRate: the time taken to complete one cycle in seconds.
    OUTPUTS:
    no returns
    """

    try:
        #get filteredTempList from input subsystem 
        global indoorFilteredTempList,outdoorFilteredTempList,lockedOut,lockeoutStartTime 
        while True:
            startTime = time.time() #Measure starting time
            filteredTemp = thermistor_inside() 
            indoorFilteredTempList.append(filteredTemp)
            outdoorFilteredTemp = thermistor_outside()
            outdoorFilteredTempList.append(outdoorFilteredTemp)

            print(fan_LED_status(filteredTemp,goalTemp,allowableTempRange,outdoorFilteredTemp))
            thermometer()
            validate_LDR_resistance(6)
            endTime = time.time()
            time.sleep(2-(endTime-startTime)) #Sleep for remaining time to make up to 2 sec
            print("2.0 sec to complete 1 polling cycle")# Polling time same for each loop 




    

    except KeyboardInterrupt:
        select_operating_mode()


#Select Operating Mode 
def select_operating_mode(): 
    """
    select_operating_mode function allows user to select which mode to enter from the 3 modes.
    INPUTS:
    None.
    OUTPUTS: 
    None.
    """

    while True:
        try:
            # formats the menu
            print("\n====================MENU====================")
            modeChoice = int(input("Select operating mode:\n(1) Normal Operation Mode\n(2) Maintanence Adjustment Mode\n(3) Data Observation Mode\n"))
            
            # enters specific mode according to given input
            if modeChoice == 1:
                print("Entering Normal Operation mode")
                norm_operating_mode(pollingRate)

            elif modeChoice == 2:
                maintainence_adjustment_mode(8888)

            elif modeChoice == 3:
                print("Entering data observation mode")
                data_observation_mode(indoorFilteredTempList=indoorFilteredTempList,outdoorFilteredTempList=outdoorFilteredTempList,pollingRate=2)
            else:
                raise ValueError
        # will run until a valid option is picked. (1,2 or 3).
        except ValueError:
            print("Invalid input, select from given operating modes")
            select_operating_mode()



select_operating_mode()
board.shutdown()