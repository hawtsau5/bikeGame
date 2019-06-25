#!bin/env python

import random
from time import sleep

import uinput
import RPi.GPIO as GPIO
import time
import math
import pygame

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.IN)
GPIO.setup(27, GPIO.IN)
GPIO.setup(21, GPIO.IN)

dist_meas = 0.00
km_per_hour = 0
rpm = 0
elapse = 0
pulse = 0
start_timer = time.time()






def calculate_elapse(channel):              # callback function
    global pulse, start_timer, elapse
    pulse+=1                                # increase pulse by 1 whenever interrupt occurred
    elapse = time.time() - start_timer      # elapse for every 1 complete rotation made!
    start_timer = time.time()               # let current time equals to start_timer

def calculate_speed(r_cm):
    global pulse,elapse,rpm,dist_km,dist_meas,km_per_sec,km_per_hour
    if elapse !=0:                          # to avoid DivisionByZero error
        rpm = 1/elapse * 60
        circ_cm = (2*math.pi)*r_cm          # calculate wheel circumference in CM
        dist_km = circ_cm/100000            # convert cm to km
        km_per_sec = dist_km / elapse       # calculate KM/sec
        km_per_hour = km_per_sec * 3600     # calculate KM/h
        dist_meas = (dist_km*pulse)*1000    # measure distance traverse in meter
        return km_per_hour

def init_interrupt():
    GPIO.add_event_detect(21, GPIO.FALLING, callback = calculate_elapse, bouncetime = 20)  

def adaptive_difficulty(last_tick_speed, current_tick_speed):
    print(current_tick_speed)
    speed_min_limit = 2
    if(last_tick_speed < current_tick_speed):
        print('increase by 1')
        return 1
    elif (last_tick_speed > current_tick_speed and current_tick_speed > speed_min_limit):
        print('decrease by 1')
        return -1
    else:
        print('no change')
        return 0
    

class CarRacing:
    def __init__(self):

        pygame.init()
        self.display_width = 800
        self.display_height = 600
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.clock = pygame.time.Clock()
        self.gameDisplay = None

        self.initialize()

    def initialize(self):

        self.crashed = False

        self.carImg = pygame.image.load("./img/car.png")
        self.car_x_coordinate = (self.display_width * 0.45)
        self.car_y_coordinate = (self.display_height * 0.8)
        self.car_width = 49
        self.previous_speed_kmph = 0
        self.current_speed_kmph = 0

        # enemy_car
        self.enemy_car = pygame.image.load('./img/enemy_car_1.png')
        self.enemy_car_startx = random.randrange(310, 450)
        self.enemy_car_starty = -600
        self.enemy_car_speed = 5
        self.enemy_car_width = 49
        self.enemy_car_height = 100

        # Background
        self.bgImg = pygame.image.load("./img/back_ground.jpg")
        self.bg_x1 = (self.display_width / 2) - (360 / 2)
        self.bg_x2 = (self.display_width / 2) - (360 / 2)
        self.bg_y1 = 0
        self.bg_y2 = -600
        self.bg_speed = 5
        self.count = 0

    def car(self, car_x_coordinate, car_y_coordinate):
        self.gameDisplay.blit(self.carImg, (car_x_coordinate, car_y_coordinate))

    def racing_window(self):
        self.gameDisplay = pygame.display.set_mode((self.display_width, self.display_height))
        pygame.display.set_caption('Car Dodge')
        self.run_car()
        

  

    def run_car(self):
        device = uinput.Device([uinput.KEY_LEFT, uinput.KEY_RIGHT, uinput.KEY_W])

        left = False
        right= False
        up = False


        while not self.crashed:
            if (not left) and (not GPIO.input(17)):
                left = True
                device.emit(uinput.KEY_LEFT, 1)
            if left and GPIO.input(17):
                left = False
                device.emit(uinput.KEY_LEFT, 0)
            if (not right) and (not GPIO.input(27)):
                right  = True
                device.emit(uinput.KEY_RIGHT, 1)
            if right and GPIO.input(27):
                right = False
                device.emit(uinput.KEY_RIGHT, 0)
                

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.crashed = True
                # print(event)

                if (event.type == pygame.KEYDOWN):
                    if (event.key == pygame.K_LEFT):
                        self.car_x_coordinate -= 50
                        print ("CAR X COORDINATES: %s" % self.car_x_coordinate)
                    if (event.key == pygame.K_RIGHT):
                        self.car_x_coordinate += 50
                        print ("CAR X COORDINATES: %s" % self.car_x_coordinate)
                    print ("x: {x}, y: {y}".format(x=self.car_x_coordinate, y=self.car_y_coordinate))

            self.gameDisplay.fill(self.black)
            self.back_ground_road()

            self.run_enemy_car(self.enemy_car_startx, self.enemy_car_starty)
            self.enemy_car_starty += self.enemy_car_speed

            if self.enemy_car_starty > self.display_height:
                self.enemy_car_starty = 0 - self.enemy_car_height
                self.enemy_car_startx = random.randrange(310, 450)

            self.car(self.car_x_coordinate, self.car_y_coordinate)
            self.highscore(self.count)
            self.count += 1
            
            if (self.count % 100 == 0):
                tick_speed = 0
                self.current_speed_kmph = calculate_speed(10.5)
                print('rpm:{0:.0f}-RPM kmh:{1:.0f}-KMH dist_meas:{2:.2f}m pulse:{3}'.format(rpm,km_per_hour,dist_meas,pulse))                
                tick_speed = adaptive_difficulty(self.previous_speed_kmph, self.current_speed_kmph)
                self.enemy_car_speed += tick_speed
                self.bg_speed += tick_speed  
                self.previous_speed_kmph = self.current_speed_kmph
                
                
#brought to you by code-projects.org
            #if self.car_y_coordinate < self.enemy_car_starty + self.enemy_car_height:
                #if self.car_x_coordinate > self.enemy_car_startx and self.car_x_coordinate < self.enemy_car_startx + self.enemy_car_width or self.car_x_coordinate + self.car_width > self.enemy_car_startx and self.car_x_coordinate + self.car_width < self.enemy_car_startx + self.enemy_car_width:
                    #self.crashed = True
                    #self.display_message("Game Over !!!")

            #if self.car_x_coordinate < 310 or self.car_x_coordinate > 460:
                #self.crashed = True
                #self.display_message("Game Over !!!")

            pygame.display.update()
            self.clock.tick(60)

    def display_message(self, msg):
        font = pygame.font.SysFont("comicsansms", 72, True)
        text = font.render(msg, True, (255, 255, 255))
        self.gameDisplay.blit(text, (400 - text.get_width() // 2, 240 - text.get_height() // 2))
        self.display_credit()
        pygame.display.update()
        self.clock.tick(60)
        sleep(1)
        car_racing.initialize()
        car_racing.racing_window()

    def back_ground_road(self):
        self.gameDisplay.blit(self.bgImg, (self.bg_x1, self.bg_y1))
        self.gameDisplay.blit(self.bgImg, (self.bg_x2, self.bg_y2))

        self.bg_y1 += self.bg_speed
        self.bg_y2 += self.bg_speed

        if self.bg_y1 >= self.display_height:
            self.bg_y1 = -600

        if self.bg_y2 >= self.display_height:
            self.bg_y2 = -600

    def run_enemy_car(self, thingx, thingy):
        self.gameDisplay.blit(self.enemy_car, (thingx, thingy))

    def highscore(self, count):
        font = pygame.font.SysFont("lucidaconsole", 20)
        text = font.render("Score : " + str(count), True, self.white)
        self.gameDisplay.blit(text, (0, 0))

    def display_credit(self):
        font = pygame.font.SysFont("lucidaconsole", 14)
        text = font.render("Thanks To Anuj,", True, self.white)
        self.gameDisplay.blit(text, (600, 520))
        text = font.render("for the", True, self.white)
        self.gameDisplay.blit(text, (600, 530))
        text = font.render("source code", True, self.white)
        self.gameDisplay.blit(text, (600, 540))
        text = font.render("Brought To You By", True, self.white)
        self.gameDisplay.blit(text, (600, 560))
        text = font.render("code-projects.org", True, self.white)
        self.gameDisplay.blit(text, (600, 570))


if __name__ == '__main__':
    init_interrupt()
    car_racing = CarRacing()
    car_racing.racing_window()
