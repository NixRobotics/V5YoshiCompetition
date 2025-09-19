#region VEXcode Generated Robot Configuration
from vex import *
import urandom
import math

# Brain should be defined by default
brain=Brain()

# Robot configuration code
left_motor_a = Motor(Ports.PORT3, GearSetting.RATIO_18_1, False)
left_motor_b = Motor(Ports.PORT4, GearSetting.RATIO_18_1, False)
left_drive_smart = MotorGroup(left_motor_a, left_motor_b)
right_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_18_1, True)
right_motor_b = Motor(Ports.PORT2, GearSetting.RATIO_18_1, True)
right_drive_smart = MotorGroup(right_motor_a, right_motor_b)
drivetrain_inertial = Inertial(Ports.PORT11)
drivetrain = SmartDrive(left_drive_smart, right_drive_smart, drivetrain_inertial, 319.19, 320, 40, MM, 1)
controller_1 = Controller(PRIMARY)
armmotor = Motor(Ports.PORT8, GearSetting.RATIO_18_1, True)
beltmotor = Motor(Ports.PORT7, GearSetting.RATIO_18_1, True)
CatchMotor = Motor(Ports.PORT6, GearSetting.RATIO_18_1, False)


# wait for rotation sensor to fully initialize
wait(30, MSEC)


# Make random actually random
def initializeRandomSeed():
    wait(100, MSEC)
    random = brain.battery.voltage(MV) + brain.battery.current(CurrentUnits.AMP) * 100 + brain.timer.system_high_res()
    urandom.seed(int(random))
      
# Set random seed 
initializeRandomSeed()

vexcode_initial_drivetrain_calibration_completed = False
def calibrate_drivetrain():
    # Calibrate the Drivetrain Inertial
    global vexcode_initial_drivetrain_calibration_completed
    sleep(200, MSEC)
    brain.screen.print("Calibrating")
    brain.screen.next_row()
    brain.screen.print("Inertial")
    drivetrain_inertial.calibrate()
    while drivetrain_inertial.is_calibrating():
        sleep(25, MSEC)
    vexcode_initial_drivetrain_calibration_completed = True
    brain.screen.clear_screen()
    brain.screen.set_cursor(1, 1)


# Calibrate the Drivetrain
calibrate_drivetrain()


def play_vexcode_sound(sound_name):
    # Helper to make playing sounds from the V5 in VEXcode easier and
    # keeps the code cleaner by making it clear what is happening.
    print("VEXPlaySound:" + sound_name)
    wait(5, MSEC)

# add a small delay to make sure we don't print in the middle of the REPL header
wait(200, MSEC)
# clear the console to make sure we don't have the REPL in the console
print("\033[2J")



# define variables used for controlling motors based on controller inputs
controller_1_left_shoulder_control_motors_stopped = True
controller_1_right_shoulder_control_motors_stopped = True
drivetrain_needs_to_be_stopped_controller_1 = False

# define a task that will handle monitoring inputs from controller_1
def rc_auto_loop_function_controller_1():
    global drivetrain_needs_to_be_stopped_controller_1, controller_1_left_shoulder_control_motors_stopped, controller_1_right_shoulder_control_motors_stopped, remote_control_code_enabled
    # process the controller input every 20 milliseconds
    # update the motors based on the input values
    while True:
        if remote_control_code_enabled:
            # stop the motors if the brain is calibrating
            if drivetrain_inertial.is_calibrating():
                left_drive_smart.stop()
                right_drive_smart.stop()
                while drivetrain_inertial.is_calibrating():
                    sleep(25, MSEC)
            
            # calculate the drivetrain motor velocities from the controller joystick axies
            # left = axis3 + axis4
            # right = axis3 - axis4
            drivetrain_left_side_speed = controller_1.axis3.position() + controller_1.axis4.position()
            drivetrain_right_side_speed = controller_1.axis3.position() - controller_1.axis4.position()
            
            # check if the values are inside of the deadband range
            if abs(drivetrain_left_side_speed) < 5 and abs(drivetrain_right_side_speed) < 5:
                # check if the motors have already been stopped
                if drivetrain_needs_to_be_stopped_controller_1:
                    # stop the drive motors
                    left_drive_smart.stop()
                    right_drive_smart.stop()
                    # tell the code that the motors have been stopped
                    drivetrain_needs_to_be_stopped_controller_1 = False
            else:
                # reset the toggle so that the deadband code knows to stop the motors next
                # time the input is in the deadband range
                drivetrain_needs_to_be_stopped_controller_1 = True
            
            # only tell the left drive motor to spin if the values are not in the deadband range
            if drivetrain_needs_to_be_stopped_controller_1:
                left_drive_smart.set_velocity(drivetrain_left_side_speed, PERCENT)
                left_drive_smart.spin(FORWARD)
            # only tell the right drive motor to spin if the values are not in the deadband range
            if drivetrain_needs_to_be_stopped_controller_1:
                right_drive_smart.set_velocity(drivetrain_right_side_speed, PERCENT)
                right_drive_smart.spin(FORWARD)
            # check the buttonL1/buttonL2 status
            # to control armmotor
            if controller_1.buttonL1.pressing():
                armmotor.spin(FORWARD)
                controller_1_left_shoulder_control_motors_stopped = False
            elif controller_1.buttonL2.pressing():
                armmotor.spin(REVERSE)
                controller_1_left_shoulder_control_motors_stopped = False
            elif not controller_1_left_shoulder_control_motors_stopped:
                armmotor.stop()
                # set the toggle so that we don't constantly tell the motor to stop when
                # the buttons are released
                controller_1_left_shoulder_control_motors_stopped = True
            # check the buttonR1/buttonR2 status
            # to control beltmotor
            if controller_1.buttonR1.pressing():
                beltmotor.spin(FORWARD)
                controller_1_right_shoulder_control_motors_stopped = False
            elif controller_1.buttonR2.pressing():
                beltmotor.spin(REVERSE)
                controller_1_right_shoulder_control_motors_stopped = False
            elif not controller_1_right_shoulder_control_motors_stopped:
                beltmotor.stop()
                # set the toggle so that we don't constantly tell the motor to stop when
                # the buttons are released
                controller_1_right_shoulder_control_motors_stopped = True
        # wait before repeating the process
        wait(20, MSEC)

# define variable for remote controller enable/disable
remote_control_code_enabled = True

rc_auto_loop_thread_controller_1 = Thread(rc_auto_loop_function_controller_1)

#endregion VEXcode Generated Robot Configuration

# ------------------------------------------
# 
# 	Project:
#	Author:
#	Created:
#	Configuration:
# 
# ------------------------------------------

# Library imports
from vex import *

# Begin project code

remote_control_code_enabled = False

# motors will slow down above certain temperatures
# vex defines warm as 50 percent and 70 percent
MOTOR_HOT_TEMP = 70
MOTOR_WARM_TEMP = 50


# this function checks the temperature of each motor and then return two values: warm, hot
def motor_temperature():
   # to make code simple we create a list of all the motors, then check each one
   allmotors = [left_motor_a, left_motor_b, right_motor_a, right_motor_b, armmotor, beltmotor]
   motor_is_warm = False
   motor_is_hot = False
   for motor in allmotors:
       if motor.temperature(PERCENT) >= MOTOR_HOT_TEMP: motor_is_hot = True
       elif motor.temperature(PERCENT) >= MOTOR_WARM_TEMP: motor_is_warm = True


   return motor_is_warm, motor_is_hot


# we run this in its own thread to monitor the temperature each second and change the color of the screen
# blue is wam
# red is hot
def monitor_motor_temperatures():
   while True:
       motor_is_warm, motor_is_hot = motor_temperature()
       if (motor_is_hot): brain.screen.clear_screen(Color.RED)
       elif (motor_is_warm): brain.screen.clear_screen(Color.BLUE)
       wait(1,SECONDS)


def pre_autonomous():
    # actions to do when the program starts
    brain.screen.clear_screen()
    brain.screen.print("pre auton code")
    wait(1, SECONDS)

remote_control_code_enabled = False
#constant for controller deadban
CONRTROLLER_DEADBAN = 5

def drivetrain_detwitch(speed, turn):   
   # reduce turn sensitiviy when robot is moving slowly (turning in place)
   speedmixLim = 50.0 # upper limit of throttle mixing (above this point, full turn allowed)
   # NOTE: Next 2 parameters should add up to 1.0 (throttlemixMinSens + throttlemixSlope = 1.0)
   speedmixMinSens = 0.35 # minimum turn sensitivity point (i.e. when turning in place)
   speedmixSlope = 0.65 # rate at which turn sensitivity increases with increased throttle
   # turnscale will be used to change how fast we can turn based on spee
   turnscale = 1.0 # start with full turn speed


   if (abs(speed) < speedmixLim):
       speedmix = abs(speed) / speedmixLim
       turnscale = turnscale * (speedmixMinSens + speedmixSlope * speedmix)


   turn = turn * turnscale


   left_speed = speed + turn
   right_speed = speed - turn


   return left_speed, right_speed


# constants to convert percent to volt for drivetrain
MOTOR_MAXVOLT = 10.9 # volts
MOTOR_VOLTSCALE = MOTOR_MAXVOLT / 100.0

def fx_user_drivetrain():
    global drivetrain_needs_to_be_stopped_controller_1
    # calculate the drivetrain motor velocities from the controller joystick axies
    # left = axis3 + axis4
    # right = axis3 - axis4
    # drivetrain_left_side_speed = controller_1.axis3.position() + controller_1.axis4.position()
    # drivetrain_right_side_speed = controller_1.axis3.position() - controller_1.axis4.position()
    drivetrain_left_side_speed, drivetrain_right_side_speed = drivetrain_detwitch(controller_1.axis3.position(), controller_1.axis4.position())

    
    # check if the values are inside of the deadband range
    if abs(drivetrain_left_side_speed) < CONRTROLLER_DEADBAN and abs(drivetrain_right_side_speed) < CONRTROLLER_DEADBAN:
        # check if the motors have already been stopped
        if drivetrain_needs_to_be_stopped_controller_1:
            # stop the drive motors
            left_drive_smart.stop()
            right_drive_smart.stop()
            # tell the code that the motors have been stopped
            drivetrain_needs_to_be_stopped_controller_1 = False
    else:
    # reset the toggle so that the deadband code knows to stop the motors next
    # time the input is in the deadband range
        drivetrain_needs_to_be_stopped_controller_1 = True

    # only tell the left drive motor to spin if the values are not in the deadband range
    if drivetrain_needs_to_be_stopped_controller_1:
        left_drive_smart.spin(FORWARD, drivetrain_left_side_speed * MOTOR_VOLTSCALE, VOLT)


        # only tell the right drive motor to spin if the values are not in the deadband range
    if drivetrain_needs_to_be_stopped_controller_1:
        right_drive_smart.spin(FORWARD, drivetrain_right_side_speed * MOTOR_VOLTSCALE, VOLT)

remote_control_code_enabled = False

# constants for arm gear ratio and motion limits
ARM_GEAR_RATIO = 48.0/24.0 * 36.0/12.0
# because of gear ratio, motor needs to spin a lot more for the arm to move by each degree
ARM_MAXIMUM_UP = 0.0 * ARM_GEAR_RATIO
ARM_MAXIMUM_DOWN = -130.0 * ARM_GEAR_RATIO

def fx_user_arm():

    # process the controller input every time this function is called
    # update the motors based on the input values
    # calculate the arm motor velocities from the controller joystick axies
    # up = axis 2 is negative
    # down = axis 2 is positive
    # note that this is opposite from the L1/L2 so we can either go to the visual code an
    # change it or we negate the control here
    armmotor_speed = -controller_1.axis2.position()

    # check if the values are inside of the deadband range
    if abs(armmotor_speed) < CONRTROLLER_DEADBAN:
        armmotor_speed = 0
    # now check if arm is at the maximum raised or lowered limit
    elif (armmotor_speed > 0 and armmotor.position(DEGREES) >= ARM_MAXIMUM_UP):
        armmotor_speed = 0
    elif (armmotor_speed < 0 and armmotor.position(DEGREES) <= ARM_MAXIMUM_DOWN):
        armmotor_speed = 0


    if (armmotor_speed == 0):
        armmotor.stop(HOLD)
    else:
        armmotor.set_velocity(armmotor_speed, PERCENT)
        armmotor.spin(FORWARD)

# constants for pusher
PUSHER_SPROCKET_SIZE = 6 # teeth
PUSHER_TRAVEL = 14 # chain lengths
PUSHER_TURNS = PUSHER_TRAVEL / PUSHER_SPROCKET_SIZE # turns

belt_speed = 0

def belt_faster():
   global belt_speed
   if belt_speed == 0: belt_speed = 25
   elif belt_speed == 25: belt_speed = 75
   beltmotor.set_velocity(belt_speed,PERCENT)
   beltmotor.spin(FORWARD)
   
def belt_slower():
   global belt_speed
   if belt_speed > 0: belt_speed = belt_speed - 25
   beltmotor.set_velocity(belt_speed,PERCENT)
   beltmotor.spin(FORWARD)

def belt_stop():
    global belt_speed
    belt_speed = 0
    beltmotor.stop()

def raise_catch():
   belt_stop()
   CatchMotor.set_velocity(100,PERCENT)
   CatchMotor.set_stopping(HOLD) 
   CatchMotor.set_timeout(2,SECONDS) 
   CatchMotor.spin_to_position(60*9,DEGREES,wait=True)
   CatchMotor.stop()


def lower_catch():
   CatchMotor.set_velocity(100,PERCENT)
   CatchMotor.set_stopping(HOLD) 
   CatchMotor.set_timeout(2,SECONDS) 
   CatchMotor.spin_to_position(0*9,DEGREES,wait=True)
   CatchMotor.stop()

def release_catch():
    CatchMotor.stop(COAST)

def controller1_buttonR1_callback():
   belt_faster()

def controller1_buttonR2_callback():
   belt_stop()

def controller1_buttonUp_callback():
    raise_catch()
    brain.screen.print("raise_catch")


def controller1_buttonDown_callback():
   lower_catch()
   brain.screen.print("lower_catch")

def controller1_buttonLeft_callback():
   release_catch()

# fx_user_control_loop_controller_1() does not get called anymore - DELETE
def fx_user_control_loop_controller_1():
    global drivetrain_needs_to_be_stopped_controller_1, controller_1_left_shoulder_control_motors_stopped, controller_1_right_shoulder_control_motors_stopped, remote_control_code_enabled
    # process the controller input every 20 milliseconds
    # update the motors based on the input values

    # code moved to fx_user_drivetrain()
    # code moved to fx_user_arm()
    # code moved to fx_user_pusher()

def user_control():
    brain.screen.clear_screen()
    # place driver control in this while loop
    #fx_user_control_loop_controller_1()

    # place callbacks here
    controller_1.buttonR1.pressed(controller1_buttonR1_callback)
    controller_1.buttonR2.pressed(controller1_buttonR2_callback)

    controller_1.buttonUp.pressed(controller1_buttonUp_callback)
    controller_1.buttonDown.pressed(controller1_buttonDown_callback)
    controller_1.buttonLeft.pressed(controller1_buttonLeft_callback)

    # check motor temperatures
    temperature_monitor_thread = Thread(monitor_motor_temperatures)

    while True:
        fx_user_drivetrain()
        fx_user_arm()
        wait(20, MSEC)
# add before autonomous()
CONVEYOR_HOOKS = 6
CONVEYOR_SPACING = 13
CONVEYOR_LINKS = 21 + (CONVEYOR_HOOKS * CONVEYOR_SPACING)
CONVEYOR_BIG_TEETH = 12

def belt_spin_one_loop(waitfordone = True):
    belt_spin_to_first(0,0,waitfordone)

def belt_spin_to_first(hooks = 0, links = 0, waitfordone = True):
    # note: must first fix wrong cartride for belt
    belt_ratio = ((CONVEYOR_LINKS - hooks * CONVEYOR_SPACING - links) / CONVEYOR_BIG_TEETH)
    beltmotor.set_velocity(85,PERCENT)
    beltmotor.spin_for(FORWARD,belt_ratio,TURNS, waitfordone)

def belt_spin_hooks(hooks = 1, waitfordone = True):
    # note: must first fix wrong cartride for belt
    belt_ratio = ((hooks * CONVEYOR_SPACING) / CONVEYOR_BIG_TEETH)
    beltmotor.set_velocity(85,PERCENT)
    beltmotor.spin_for(FORWARD,belt_ratio,TURNS, waitfordone)

def left_turn_adjust(turn_in):
    return turn_in

def right_turn_adjust(turn_in):
    return turn_in

def lower_arm(angle1):
    armmotor.set_velocity(100,PERCENT)
    armmotor.spin_for(REVERSE,6*angle1,DEGREES)
    armmotor.stop()

AUTON_SKILLS = 1
AUTON_MATCH_LEFT = 2
AUTON_MATCH_RIGHT = 3
AUTON_MATCH_NONE = 4

WHICH_AUTON = AUTON_SKILLS

def autonomous():
    if WHICH_AUTON == AUTON_SKILLS:
        autonomous_skills()
    elif WHICH_AUTON == AUTON_MATCH_LEFT:
        autonomous_match_left()
    elif WHICH_AUTON == AUTON_MATCH_RIGHT:
        autonomous_match_right()
    else:
        autonomous_none()

def autonomous_none():
    brain.screen.clear_screen()
    brain.screen.print("autonomous code")
    drivetrain.drive_for(REVERSE, 8, INCHES)
    drivetrain.stop()
    brain.screen.print("autonomous done")

def autonomous_match_left():
    brain.screen.clear_screen()
    brain.screen.print("autonomous code")

    raise_catch()
    drivetrain.set_stopping(COAST) #softer stop
    drivetrain.set_drive_velocity(65, PERCENT)
    drivetrain.drive_for(REVERSE, 33, INCHES)
    drivetrain.turn_for(RIGHT, 90, DEGREES)
    drivetrain.set_drive_velocity(25, PERCENT)
    drivetrain.drive_for(REVERSE, 8, INCHES)
    lower_catch()
    belt_spin_one_loop(False)
    drivetrain.turn_for(RIGHT, 90, DEGREES)
    drivetrain.drive_for(FORWARD, 11.5, INCHES)
    drivetrain.stop()


    brain.screen.print("autonomous done")

def autonomous_match_right():
    brain.screen.clear_screen()
    brain.screen.print("autonomous code")
    # place automonous code here
    raise_catch()
    drivetrain.set_stopping(COAST) #softer stop
    drivetrain.set_drive_velocity(65, PERCENT)
    drivetrain.drive_for(REVERSE, 33, INCHES)
    drivetrain.turn_for(LEFT, 90, DEGREES)
    drivetrain.set_drive_velocity(25, PERCENT)
    drivetrain.drive_for(REVERSE, 8, INCHES)
    lower_catch()
    belt_spin_one_loop(False)
    drivetrain.turn_for(LEFT, 90, DEGREES)
    drivetrain.drive_for(FORWARD, 11.5, INCHES)
    drivetrain.stop()


    brain.screen.clear_screen()
    brain.screen.print("autonomous done")
    
def autonomous_skills():
    brain.screen.clear_screen()
    brain.screen.print("autonomous code")
    # place automonous code here
    #preload in + catching mobile goal

    ## ------- FIRST MOBILE GOAL --------- ##

    # initial reverse from wall
    drivetrain.set_stopping(COAST) #softer stop
    drivetrain.set_drive_velocity(33, PERCENT)
    raise_catch()
    drivetrain.drive_for(REVERSE, 14.5, INCHES) ## - changed: move back just a little more
    
    # point catch towards goal and reverse
    wait(0.1,SECONDS) # after drive - short pause before turning to let things settle
    drivetrain.turn_for(LEFT, 90, DEGREES) # first turn seems very picky 90 * left_turn_adjust
    left_drive_smart.spin_for(FORWARD,24,DEGREES) # small nudge
    drivetrain.set_drive_velocity(25, PERCENT)
    
    drivetrain.drive_for(REVERSE, 19,INCHES)
    
    lower_catch()
    belt_spin_to_first(1, 3, False) # we are one hook and 3 chain links into full loop

    ## ------- FIRST FLOOR DONUT --------- ##

    # turn around and drive towards first donut
    drivetrain.set_drive_velocity(33, PERCENT)
    drivetrain.set_heading(270,DEGREES)
    drivetrain.turn_for(LEFT, left_turn_adjust(180), DEGREES) # left_180_loaded * left_turn_adjust
    left_drive_smart.spin_for(FORWARD,12,DEGREES)
    drivetrain.drive_for(FORWARD, 20, INCHES)

    # pickup donut
    belt_spin_one_loop()

    ## ------- SECOND FLOOR DONUT --------- ##

    # second donut
    drivetrain.set_drive_velocity(33, PERCENT)
    drivetrain.drive_for(FORWARD, 14, INCHES)
    drivetrain.set_drive_velocity(33, PERCENT)

    # intake
    belt_spin_hooks(2)
    # start moving while we complete loading
    # -- old belt_spin_to_first(2,0,False)
    belt_spin_one_loop(False) # this is more reliable in case intake doesn't work first time

    ## ------- PLACE MOBILE GOAL --------- ##

    # point goal towards corner and reverse in
    wait(0.1,SECONDS)
    drivetrain.set_heading(270.0, DEGREES)
    drivetrain.turn_for(RIGHT,right_turn_adjust(90),DEGREES)
    right_drive_smart.spin_for(FORWARD, 24, DEGREES)
    
    drivetrain.drive_for(REVERSE, 6, INCHES)
    # drivetrain.drive_for(FORWARD, 1, INCHES)

    wait(0.1, SECONDS)
    drivetrain.turn_for(RIGHT, right_turn_adjust (37.5), DEGREES)
    right_drive_smart.spin_for(FORWARD, 24, DEGREES)
    raise_catch()
    drivetrain.drive_for(FORWARD, 6, INCHES)
    lower_catch()
    drivetrain.drive_for(REVERSE, 10, INCHES)
    drivetrain.drive_for(FORWARD, 9, INCHES) ## -- changed: make sure we're properly in the center

    # should now be back at the tile intersection
    # turn and drive to next mogo
    wait(0.1,SECONDS)
    drivetrain.turn_to_heading(90, DEGREES)
    right_drive_smart.spin_for(FORWARD,24,DEGREES)
    drivetrain.set_drive_velocity(50, PERCENT)
    belt_spin_to_first(2,0,False) # -- new: need to add spin to get to first hook
    drivetrain.drive_for(FORWARD, 47+5, INCHES) # -- changed: make sure we're at the center

    ## ------- HALF WAY --------- ##

    # while not controller_1.buttonX.pressing():
    #    wait(0.01, SECONDS)

    ## ------- SECOND MOBILE GOAL --------- ##

    drivetrain.set_drive_velocity(33, PERCENT)
    drivetrain.set_heading(0, DEGREES)
    wait(0.1, SECONDS)
    drivetrain.turn_for(LEFT, 180, DEGREES) # left_180_loaded * left_turn_adjust
    raise_catch()
    drivetrain.set_drive_velocity(25, PERCENT)
    right_drive_smart.spin_for(REVERSE, 24, DEGREES)
    drivetrain.drive_for(REVERSE, 20, INCHES)
    lower_catch()
    drivetrain.set_drive_velocity(33, PERCENT)

    ## ------- THIRD DONUT --------- ##

    # point towards next donut and drive towards it
    drivetrain.turn_for(LEFT, 180, DEGREES) #left_180_loaded * left_turn_adjust
    left_drive_smart.spin_for(FORWARD, 12, DEGREES)
    drivetrain.drive_for(FORWARD, 22, INCHES)

    # intake donut and then load on mogo
    # pickup donut
    belt_spin_one_loop()

    ## ------- FOURTH DONUT --------- ##

    # second donut on right
    drivetrain.set_drive_velocity(33, PERCENT)
    drivetrain.drive_for(FORWARD, 14, INCHES) # -- changed: was driving too far
    drivetrain.set_drive_velocity(33, PERCENT)

    # intake
    belt_spin_hooks(2)
    # start moving while we complete loading
    belt_spin_one_loop(False) ## -- changed: more reliable

    ## ------- SECOND MOBILE GOAL --------- ##

    #turn so mogo is pointing towards corner and release it
    wait(0.1, SECONDS)
    drivetrain.set_heading(90.0, DEGREES)
    drivetrain.turn_for(LEFT, left_turn_adjust(90), DEGREES)
    #right_drive_smart.spin(FORWARD, 24, DEGREES)
    # belt_spin_hooks(2, False) ## -- old: replaced with full spin above
    drivetrain.drive_for(REVERSE, 6, INCHES)
    wait(0.1, SECONDS)
    drivetrain.turn_for(LEFT, left_turn_adjust(30), DEGREES)
    right_drive_smart.spin_for(FORWARD, 24, DEGREES)
    raise_catch()
    drivetrain.drive_for(FORWARD, 6, INCHES)
    lower_catch()
    drivetrain.drive_for(REVERSE, 10, INCHES)
    drivetrain.drive_for(FORWARD, 8, INCHES)

    ## ------- DONE --------- ##

    drivetrain.stop()

    brain.screen.clear_screen()
    brain.screen.print("autonomous done")
    
# create competition instance
comp = Competition(user_control, autonomous)
pre_autonomous()