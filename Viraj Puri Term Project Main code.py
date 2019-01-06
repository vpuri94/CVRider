import cv2
import sys
import datetime as dt
from time import sleep
import pygame
import random
import math
import pygame.time
from tkinter import *
from scratch import InputBox
import pygame as pg
####################






######################

pygame.init()
#if game doesnt work properly, try lowering resolution (i.e to 1280x720) 
screenWidth = 1920
screenHeight = 1080
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screenWidth, screenHeight))


heroPic = pygame.image.load("rider.png").convert_alpha()
background = pygame.image.load("background.png").convert_alpha()
blue = (0,0,255) #sets up the colors to manipulate the background/obstacles
#/power ups
red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)
black = (0, 0, 0)
purple = (138,43,226)
fps = 60
timer = 1
timer1 = 0
num = 1
#above all variables are initialized

#below, all the fonts, and rendered forms to actually display them are made


introFont = pygame.font.SysFont("arial", 30)

playFont = pygame.font.SysFont("arial", 36)
renderedPlay = playFont.render("Play", 1, black) 
renderedInstructions = playFont.render("Instructions", 1, black)

buildingFont = pygame.font.SysFont("arial", 36)

largeFont = pygame.font.SysFont("arial", 72)

renderedIntro = largeFont.render("Welcome to CVRider!", 1, red)

veryLargeFont = pygame.font.SysFont("arial", 120)
renderedWarning = veryLargeFont.render("PLEASE PUT FACE BACK ON SCREEN", 1, white)

introCount = 5
endingCount = 5


speedingTimer = 0 
riderIsSpeeding = False

score = 0
scoreMultiplier = 1

screen_rect = screen.get_rect()

pygame.mixer.music.load("butterflyeffect.mp3")

userName = ""

buildingCoords = []
ringCoords = []

video_capture = cv2.VideoCapture(0) 
video_capture.set(3, 640)
video_capture.set(4, 480)

####
cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
    

##
    
dX = 0
dY = 0

###################################
isStart = True
isGame = False
isGameOver = False
#^^^For the 3 game states


#building class for each of the rectangles

class Building(object):
    def __init__(self, topX, topY, width, height, isHittable = False, timeBefore = 2):
        self.topX = topX
        self.topY = topY
        self.width = width
        self.height = height
        self.isHittable = isHittable
        self.timeBefore = timeBefore
        self.canGrow = True
        self.centerX = self.topX + (self.width//2)
        self.centerY = self.topY + (self.height//2)
    #true if the buildings area is less than a certain size    
    def itCanGrow(self):
        if(self.canGrow == False):
            return False
        if(screenWidth>self.topX > 0 or self.topX + self.width > 0):
            return True 
        self.canGrow = False
        return False
        
    #returns tuple of the x, y of top left of building, and width/height     
    def getCoords(self):
        return (self.topX, self.topY, self.width, self.height)

    def setCoords(self, newX, newY, newWidth, newHeight):
        self.topX = newX
        self.topY = newY
        self.width = newWidth
        self.height = newHeight
    #after spawning, you have a certain time before its actually in your view to be able to be hit
    def buildingMessage(self):
        if(self.timeBefore > 0):
            return buildingFont.render("Avoid building in: " + str(self.timeBefore), 1, black)
        else:
            self.isHittable = True
            return buildingFont.render("DONT TOUCH BUILDING", 1, green) 

    #if the position of the rider is inside the building, then the rider has run into the building
    def riderHasHitBuilding(self, riderX, riderY):
        if(self.isHittable == False):
            return False
        else:
           
            if(self.width >0):
                if(self.topX < riderX < self.topX + self.width and self.topY < riderY < self.topY + self.height):
                    return True
            if(self.width <0):
                if(self.topX + self.width <riderX + 50 < self.topX and self.topY < riderY < self.topY + self.height):
                    return True
            return False
            
            
#makes blue speedUpRings that can increase your speed, and give you a score boost            
class speedUpRing(object):
    def __init__(self, centerX, centerY, radius = 100, isWithin = False):
        self.centerX = centerX
        self.centerY = centerY
        self.radius = radius
        self.isWithin = isWithin
        
    
#Once the rider is within the range of the ring, then he speeds up
#But if hes already speeding up, he cant get a "second" boost from being in the ring
    def riderInRing(self, riderX, riderY):
        if(riderIsSpeeding == True):
            return False
        if(self.centerX - self.radius < riderX < self.centerX + self.radius and self.centerY - self.radius < riderY < self.centerY + self.radius):
            self.isWithin = True
            return True
        self.isWithin = False
        return False
        

#spawns a coodinate of the center of a ring anywhere on the screen to be visible        
def spawnRingCoords():
    randX = random.randint(100, screenWidth - 100)
    randY = random.randint(100, screenHeight - 100)
    
    return (randX, randY)


#The intro cursor is drawn on the screen as a function of the difference in how much your face has moved from the center of the camera
def introCursor(dx, dy):
   
    screen.blit(renderedCount, (dx - 10, dy - 20))
    pygame.draw.circle(screen, red, (dx, dy), 20, 5)
    
def endingCursor(dx, dy):
    renderedReplayCount = countFont.render(str(endingCount), 1, purple) 
    screen.blit(renderedReplayCount, (dx - 10, dy - 20))
    pygame.draw.circle(screen, red, (dx, dy), 20, 5)

def putHeroOnScreen(dx, dy):
    screen.blit(heroPic, (dx, dy))
    
    
#spawns random building coordinates 
def spawnBuildingCoords():
    randX = random.randint(screenWidth //4, 3 * (screenWidth //4))
    randY = random.randint(screenHeight // 2, screenHeight - (screenHeight // 10))
    randWidth = random.randint(1,2)
    randHeight = random.randint(1,2)
    return (randX, randY, randWidth, randHeight)
    

#Gets slope to use so that the shifted x,y for the buildings can be determined
def zoomXandY(randX, randY):
    thetaXDistance = (randX - screenWidth//2)  
    thetaYDistance = (screenHeight - randY)
    thetaOne = math.atan(thetaXDistance/thetaYDistance)
    thetaTwo = math.radians(90) - thetaOne
    slope = (math.tan(thetaTwo))
    shiftedX = 10 / slope
    shiftedY = 10
    return (shiftedX, shiftedY)

    
def getLargestFace(faces):
    tempFaces = []
    finalFaces = []
    for (x,y,w,h) in faces:
        tempFaces += [(x,y,w,h)]
    largestArea = 0
    
    for coords in tempFaces:
        if((coords[2] * coords[3]) > largestArea):
            largestArea = coords[2] * coords[3]
            finalFaces = (coords[0], coords[1], coords[2], coords[3])
            
    return finalFaces
            
 
#####

def main():
    clock = pg.time.Clock()
    input_box1 = InputBox(screenWidth // 2 - 70, screenHeight // 2 + (screenHeight // 12), 140, 32)
    input_boxes = [input_box1]
    done = False

    while not done:
        screen.blit(background, (0,0))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            for box in input_boxes:
                if(type(box.handle_event(event)) == str):
                    userName = box.handle_event(event)
                    done = True

        for box in input_boxes:
            box.update()
        screen_rect = screen.get_rect()
        renderedDisplay = largeFont.render("Please enter your username then press enter!", True, black)
        instructions = renderedDisplay.get_rect()
        instructions.center = screen_rect.center
        screen.blit(renderedDisplay, instructions)
        for box in input_boxes:
            box.draw(screen)


        pg.display.flip()
        clock.tick(30)
    return userName    
        
 
########
 
#Crates a neat little dictionary of the high scores
def makeDictOfHighScores(filename):
    scoreDictionary = {}
    scoreFile = open(filename)
    for player in scoreFile:
        newPlayer = player[:player.index(":")]
        score = player[player.index(":") + 1:player.index("\n")]
        if(newPlayer in scoreDictionary):
            if(int(score) > int(scoreDictionary[newPlayer])):
                scoreDictionary[newPlayer] = int(score)
        else:
            scoreDictionary[newPlayer] = int(score)
    return scoreDictionary
    
    
#recursively draws window-ish looking things on right side buildings
def recursiveBuilding(x, y, width, height):
    if(width <= 50):
        return pygame.draw.rect(screen, red, (x, y, width, height), 5)
    else:
        pygame.draw.rect(screen, red, (x, y, width, height), 5)
        recursiveBuilding(x + 25, y + 25, width - 50,height - 50)

        
    
def getTop3Scores(scoreDictionary):
    finalScores = ""
    counter = 0
 
    for key in sorted(scoreDictionary.keys(), key = scoreDictionary.get, reverse = True):
        counter += 1
        if(counter > 3):
            break
        else:
            finalScores += str(counter) + ". " + key + ": " + str(scoreDictionary[key]) + " " 
    
    return finalScores
    
    
pygame.mixer.music.play(-1, 5.0)
userName = main()
while True:
    screen.blit(background, (0,0))



    # Capture frame-by-frame
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #gets the coords of an object as a list of rectangles
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    
    #Gets the face and intializes it
    myFace = getLargestFace(faces)
    if(len(myFace) > 0):
        x = myFace[0]
        y = myFace[1]
        w = myFace[2]
        h = myFace[3]
        a = (x + (w//2))
        b = (y + (h //2))
        
        dX = a - 320 #uses the dX dY of how much you moved your face from the center based on my computers 640 x 480 webcam
        dY =  b - 240
        cv2.rectangle(frame, (x, y), (x+w, y+h), green, 2)
    # Draw a rectangle around the faces
   
    if(len(faces) == 0):
        #if it doesnt detect your face in the webcams view
        #it'll tell you to put your face back in the view
       
        renderedWarning_rect = renderedWarning.get_rect()
        renderedWarning_rect.topleft = screen.get_rect().topleft
        screen.blit(renderedWarning, renderedWarning_rect)
        
         
    #allows you to break out of infinite loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    cv2.imshow('Video', frame)
    
    #print(dX, dY)
    time = clock.tick(fps) #similar to timerDelay
    
    
    
    #pygame background is a loaded image
    
    if(isStart == True):
      
        countFont = pygame.font.SysFont("arial", 35)
        renderedCount = countFont.render(str(introCount), 1, purple)
        #puts the welcome message on the screen
        
        
        welcomeMessage = renderedIntro.get_rect()
        welcomeMessage.center = screen_rect.center
        screen.blit(renderedIntro, welcomeMessage)
    #######
   
        playButton = pygame.draw.rect(screen, (153, 255, 204), (welcomeMessage.bottomleft[0], welcomeMessage.bottomleft[1] + 20, 180, 80))
        renderedPlay_rect = renderedPlay.get_rect()
        renderedPlay_rect.center = playButton.center
        
      ##################  
        
        screen.blit(renderedPlay, renderedPlay_rect)
        #puts the intro cursor on the screen
        introCursor((screenWidth//2 - 9*dX), screenHeight // 2 + 8*dY)
        time = pygame.time.get_ticks()
        if(playButton.right > ((screenWidth//2 - 9*dX)) > (playButton.left) and playButton.bottom > (screenHeight//2 + 8*dY) > (playButton.top)):
            timer += 1
            if(timer % 15 == 0):
                introCount -= 1
                #once youve held the cursor on the play button for 5 secs it starts the game
                if(introCount == 0):
                    isGame = True
                    timer = 1
                    isStart = False
        else:
            introCount = 5
        
        
        
    #main gameplay state
    if(isGame == True):
        #starts hero at center of screen and moves him accordingly
        #dX dY of the heros position
        posX = screenWidth // 2  - (10 * dX)
        posY = screenHeight // 2 + (9 * dY)
        putHeroOnScreen(posX, posY)
        if(riderIsSpeeding): #makes the timer go up if the rider is currently speeding
            timer = timer1
            timer1 += num
        else:
            timer += num
        if(timer % 45 == 0): #every 15 on the timer is 1 sec, so every 3 secs a new building is spawned
            coords = spawnBuildingCoords()
            #BUT, not if the rider is currently there as we dont want a building spawned where the rider is
            if(coords[0] + coords[2] > posX + 20 > coords[0] and coords[1] + coords[3] > posY + 40 > coords[1]):
                coords = spawnBuildingCoords()
                
            #not if there currently is a building there
            if(buildingCoords != []):#or if it could potentially collide with a building already on screen
                for build in buildingCoords:
                    if(build[0].topX < coord[0] < build[0].topX + build[0].width and build[0].topY < coord[1] < build[0].topY +build[0].height):
                        coords = spawnBuildingCoords()

            #adds that building to the list of current buildings on screen 
                  
            building = Building(coords[0], coords[1], coords[2], coords[3])
            zoomShifts = zoomXandY(coords[0] + (coords[2]//2), coords[1] + (coords[3]//2))
            buildingCoords += [(building, building.timeBefore, zoomShifts)]
        
    
        #for all the actual buildings, itll draw the building, as well as the message
        for b in buildingCoords:
            if(b[0].width > 0):
                recursiveBuilding(b[0].topX + 25, b[0].topY + 25, b[0].width - 50,b[0].height - 50)
            coord = b[0].getCoords()
            building = pygame.draw.rect(screen, red, coord, 10)
            message_rect = b[0].buildingMessage().get_rect()
            message_rect.center = building.center
            if(abs(b[0].width) > 64 and b[0].height > 36):
                if(b[0].topX + b[0].width < screenWidth or b[0].topX> 0):
                    screen.blit(b[0].buildingMessage(), message_rect)
            if(b[0].riderHasHitBuilding(posX, posY)): #checks if the rider has hit any of the buildings, then game is over
                timer = 1
                isGameOver = True
                isGame = False
            if(b[0].topX + (b[0].width//2) < 0 or b[0].topY + 30 <0):
                buildingCoords.remove(b)
            if(timer % 15 == 0):    #every second, the timeBefore you can hit the building decreases
                b[0].timeBefore -= 1
            else:
                continue
       
                
        
        #every 4 seconds a speedupring is spawned
        if(timer % 60 == 0):
            ringCoord = spawnRingCoords()
            ring = speedUpRing(ringCoord[0], ringCoord[1])
            ringCoords += [ring]
            
        if(ringCoords != []):
            for ring in ringCoords:#actually goes through and draws them
                pygame.draw.circle(screen, (10, 40, 255), (ring.centerX, ring.centerY), 100, 10)
                
                #the rider has hit a ring, speed him up, make his score increase faster, and remove that ring from the screen
                if(ring.riderInRing(posX, posY)):
                    num = 1.5
                    riderIsSpeeding = True
                    ringCoords.remove(ring)

        #actually does all the increasing for the factors if the rider is speeding 
        if(riderIsSpeeding):
            speedingTimer += 1
            scoreMultiplier = 3
            
        #after 5 seconds of speeding up, the rider slows back down    
        if(speedingTimer == 75):
            riderIsSpeeding = False
            scoreMultiplier = 1
            speedingTimer = 0 
            
        
    
        for building in buildingCoords:
            if(building[0].canGrow):
                if(building[0].topX >= screenWidth//2):
                    building[0].topX += building[2][0]
                    building[0].centerX += building[2][0]
                    building[0].width += 10 * (1.5 - (1.5 % num))
                if(building[0].topX < screenWidth//2):
                    building[0].topX += building[2][0]
                    building[0].centerX += building[2][0]
                    building[0].width += -10 * (1.5 - (1.5 % num))
                building[0].topY -= building[2][1]
                building[0].centerY  -= building[2][1]
                building[0].height += 20  * (1.5 - (1.5 % num))
                if(building[0].topY + building[0].height >= screenHeight):
                    building[0].height = screenHeight - building[0].topY 
                    
            
        #Allows only 1 speed up ring on the screen at a time        
        while(len(ringCoords) > 1):
            ringCoords.pop(0)
        
        #keeps track of score on top left
        score += (1 * scoreMultiplier)
        renderedScore = largeFont.render("Your current score: " + str(score), 1, black)
        screen.blit(renderedScore, (0,0)) 
        
       
    #Once you crash
    if(isGameOver):
        
        #######
 
        nameScore = userName + ":" + str(score) + "\n"
        highScoreFile = open("highScores.txt", "a+")
        if((nameScore in open("highScores.txt").read()) == False):
            highScoreFile.write(nameScore)
            
        #######
        scoreDict = makeDictOfHighScores("highScores.txt")
        screen.blit(background, (0,0))
        renderedFinalScore = largeFont.render("YOUR SCORE: " + str(score), 1, black)
        screen_rect = screen.get_rect()
        renderedScoreBoard = largeFont.render(getTop3Scores(scoreDict), True, black)
        scores = renderedScoreBoard.get_rect()
        scores.center = screen_rect.center
        screen.blit(renderedFinalScore, (0, 60))
        screen.blit(renderedScoreBoard, scores)
                
        renderedReplay = largeFont.render("Quit", 1, black)        
        quitButton = pygame.draw.rect(screen, (153, 255, 204), (scores.bottomleft[0], scores.bottomleft[1], 180, 80))
        renderedReplay_rect = renderedReplay.get_rect()
        renderedReplay_rect.center = quitButton.center
        
      ##################  
        
        screen.blit(renderedReplay, renderedReplay_rect)
        endingCursor((screenWidth//2 - 9*dX), screenHeight // 2 + 8*dY)
        if(quitButton.right > ((screenWidth//2 - 9*dX)) > (quitButton.left) and quitButton.bottom > (screenHeight//2 + 8*dY) > (quitButton.top)):
            timer += 1
            if(timer % 15 == 0):
                endingCount -= 1
                #once youve held the cursor on the play button for 5 secs it starts the game
                if(endingCount == 0):
                    break
        else:
            endingCount = 5
        
    pygame.display.update() #actually display the game
    

pygame.quit()

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
