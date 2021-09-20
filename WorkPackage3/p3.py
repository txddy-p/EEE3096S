# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time
# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()
count=0
guess_amount=0
value = 0
new_score = None


# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")


# Print the game menu
def menu():
    global end_of_game
    global value
    global guess_amount
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        guess_amount=0
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    for i in range(3):
        print(str(i+1)+" - "+str(raw_data[i][0])+" took "+str(raw_data[i][1])+" guesses")
    pass


# Setup Pins
def setup():
    global buzz
    global accurate
    # Setup board mode  which is tell the board you want to use physical pin numbers
    GPIO.setmode(GPIO.BOARD)
    # Setup regular GPIO
    """GPIO.setup(11, GPIO.OUT)
    GPIO.setup(13, GPIO.OUT)
    GPIO.setup(15, GPIO.OUT)"""
    #GPIO.setup(32, GPIO.OUT)
    # Setup PWM channels
    GPIO.setup(LED_value, GPIO.OUT)
    GPIO.output(LED_value, 0)
    GPIO.setup(LED_accuracy, GPIO.OUT)
    GPIO.setup(btn_increase, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_submit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(btn_increase, GPIO.FALLING, callback=btn_increase_pressed, bouncetime=500)
    GPIO.add_event_detect(btn_submit, GPIO.FALLING, callback=btn_guess_pressed, bouncetime=500)
    #pwm=GPIO.PWM(33,1000)
    # Setup debouncing and callbacks
    GPIO.setup(buzzer, GPIO.OUT)
    buzz = GPIO.PWM(buzzer, 1000)
    buzz.start(0)
    GPIO.setup(LED_accuracy, GPIO.OUT)
    accurate = GPIO.PWM(LED_accuracy,1000)
    accurate.start(0)
    pass

def main2():
    import sys
    print("argv was", sys.argv)
    print("sys.executable was", sys.executable)
    print("Restarting")
    os.execv(sys.executable, ['python3'] + sys.argv)

# Load high scores
def fetch_scores():
    # get however many scores there are
    # Get the scores
    scores, score_count = [], (eeprom.read_byte(0))
    # convert the codes back to ascii
    # return back the results
    for i in range(score_count):
        word = ""
        a = eeprom.read_block(i+1,4,16)
        for j in range(3):
            word = word + chr(a[j])
        scores.append([word,a[3]])

    return score_count, scores


# Save high scores
def save_scores():
    #global new_scores
    # fetch scores
    score_count, scores = fetch_scores()
    eeprom.write_byte(0,score_count+1)
    scores.append(new_score)
    scores.sort(key=lambda x: x[1])
    for i, score in enumerate(scores):
        data_to_write = []
            # get the string
        for letter in score[0]:
            data_to_write.append(ord(letter))
        data_to_write.append(score[1])
        eeprom.write_block(i+1, data_to_write)

    # include new score
    # sort
    # update total amount of scores
    # write new scores
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    global count
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    options = {0:[0,0,0],1:[0,0,1],2:[0,1,0],3:[0,1,1],4:[1,0,0],5:[1,0,1],6:[1,1,0],7:[1,1,1]}
    GPIO.output(LED_value, ord(chr(count)))
    if GPIO.input(btn_increase)==0:
        count = count +1
        if count in options:
            GPIO.output(LED_value[0], options[count][2])
            GPIO.output(LED_value[1], options[count][1])
            GPIO.output(LED_value[2], options[count][0])
        if GPIO.input(btn_increase)==0 and count==8:
            count = 0
            GPIO.output(LED_value, GPIO.LOW)


    pass


# Guess button
def btn_guess_pressed(channel):
    global guess_amount
    global new_score
    global count
    start_time = time.time()
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    # Change the PWM LED
    while GPIO.input(channel)==0:
        pass
    buttonTime = time.time() - start_time
    if buttonTime <= 2: # and GPIO.input(btn_submit)==0:
        trigger_buzzer()
        accuracy_leds()
        guess_amount+=1
        if count==value:
            print("Please enter your name!!")
            new_score = input()
            new_score = [new_score, guess_amount]
            print(new_score)
            save_scores()
            main2()
    else:
        print("Long")
        os.system('clear')
        main2()
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    pass


# LED Brightness
def accuracy_leds():

    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
    p = 0
    if (count-value)<0:
        p = (count/value)*100
        accurate.start(p)
    elif (count-value)>0:
        p = ((8-count)/(8-value))*100
        accurate.start(p)
    #else:
     #   accurate.start(0)

    pass

# Sound Buzzer
def trigger_buzzer():
    if abs(count-value)==1:
        buzz.ChangeFrequency(4)
        buzz.start(50)
    elif abs(count-value)==2:
        buzz.ChangeFrequency(2)
        buzz.start(50)
    elif abs(count-value)==3:
        buzz.ChangeFrequency(1)
        buzz.start(50)
    #elif count==value:
     #   buzz.start(0)

    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    pass


if __name__ == "__main__":
    #main()
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
