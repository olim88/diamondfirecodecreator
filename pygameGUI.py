#pygame GUI maker for python
#by milo
#V 1.0.0
#inport modules
import time
import pygame
#create the main veriables that are use in the code for the gui to be made that need to be able to be change for every thing in the project
DEBUG = False
showGui = True
hasUpdated = {}
usingMouse = True
groupSurfaces = {}
fontcache = {} # a chache of all created fonts so that they can be used agin 
allGui = []
events = []

# set the veriables to define the mouses infomation
mouseX = None
mouseY = None
mouseOldXY = None
mouseButtons = None
mouseOldButtons = None
mouseColison = None
mouseColison = pygame.Surface((1, 1),pygame.SRCALPHA) # get the hit box for the mouse
mouseColison.fill((100,120,100)) # fill the surfase so it can colid with the GUI
mouseColison = pygame.mask.from_surface(mouseColison)
# defalte colors and settings
textColor = (211,211,223)
backgroundColor = (24,24,27)
outlineColor = (14,14,16)
font = "Inter Medium" #Century Gothic, Inter Medium

#main definitions
def updateGui():# update the gui and show it on the windonw
    updateMouse()
    for part in allGui:
        try:
            if part.visable:
                part.update()
            elif part.selected: # if the part is a button make sure it is not pressed down
                part.click = False
                part.selected = False
                
        except: #if the part is not a button it will not get changed
            pass

def displayGui(win,group): #display the gui group
    global hasUpdated
    if showGui:
        if hasUpdated[group]:
            for part in allGui:
                if part.visable and part.group == group: # check if the part of the gui wants to be renderd and if its in the group currently being rendered
                    part.render(win)

            hasUpdated["group"]=False
        
        else:
            for part in allGui:
                if part.visable and part.group == group:
                    part.render(win)

def clearGuiGroup(group):   
    global allGui
    newGui = allGui
    for index, part in enumerate(allGui):
        if part.group == group:
            allGui = newGui.pop(index)
    allGui = newGui
def updateMouse():
    global  mouseButtons, mouseOldButtons,mouseX, mouseY
    if bool(pygame.mouse.get_focused()) and usingMouse : # check to seeif the mouse is on the screen, and the user want the mouse input to be taken
        mouseX, mouseY = pygame.mouse.get_pos() # get the new postion of the mouse
        mouseOldButtons = mouseButtons
        mouseButtons = pygame.mouse.get_pressed()
    else:
        mouseButtons = None
        mouseOldButtons = None

def createGroupSerface(group): # create a surface for a grop that is render when nothing is updated
    global groupSurfaces
    x = 1920
    y = 1080
    bigestX = 0
    bigestY = 0
    for part in allGui:
        if part.group == group:
            if part.x< x:
                x = part.x
            if part.y< y:
                y = part.y 
            if bigestX < part.x +part.width:
                bigestX = part.x +part.width
            if bigestY < part.y +part.height:
                bigestY = part.y +part.height
    width = bigestX - x 
    height = bigestY - y 
    groupSurfaces[group] =  [pygame.Surface((width, height),pygame.HWSURFACE | pygame.DOUBLEBUF| pygame.SRCALPHA),x,y] # make the surface
    groupSurfaces[group][0].convert_alpha()
    
def getOutlineWidth(width,height): # calculates a sutible outline width
    if width < height:
        outline = width/30 
    else:
        outline = height/30    
    if outline == 0 :
            outline =1
    return int(outline)

def getLargetsFont(maxHeight,fontType,importedFont,maxWidth = -1,text = "",textColor=(0,0,0)):
    outFont = None 
    i = int(round(maxHeight,0))
    neg = 10   
    while i >0:    
        i -= neg        
        if (str(i)+fontType) in fontcache:                       
            outFont = fontcache[str(i)+fontType]
        else:
            if importedFont : # if a system font is used or a file 
                outFont = pygame.font.Font(fontType, i,)                    
            else:
                outFont = pygame.font.SysFont(fontType, i, True)
            fontcache[str(i)+fontType] = outFont
        if text == "":
            Outtext = outFont.render("H|y", 1, (0,0,0)) # create a section of text to test the hight being the right size
        else:
            Outtext = outFont.render(text, 1, textColor)
        if Outtext.get_height()<= maxHeight and (Outtext.get_width()<=maxWidth or maxWidth == -1):#once the correct hight is found break for the next part of text rendering to be done
            if neg == 1:
                break
            else:
                neg = 1
                i += 9
    
    return outFont,Outtext

# elements
class button():
    def __init__(self,group,x,y,width =None,height=None,visable = True,imageLocate = None,text = None,outline= True,background = True,clickShrink = True, hoverGrow = True,shape = "rectangle",textColor = textColor, backgroundColor = backgroundColor,outlineColor = outlineColor, fontType = font, rotation = 0,transparency = 255,oneClick = False,DefocusClick = False,ExtraClickLocation =None,complexColision = False ):
        global allGui
        allGui.append(self)
        self.group = group
        self.visable = True
        self.x = x 
        self.y = y
        self.xOfset = 0
        self.yOfset = 0
        self.renderdOfsetX= 0 # an ofset if the button is renderd in a difrent place 
        self.renderdOfsetY= 0
        self.widthMultiplyer = 1
        self.heightMultiplyer = 1
        self.rotation = rotation
        self.selected = False
        self.click = False
        self.ExtraClickLocation = ExtraClickLocation #if the button is on another surface and you only want the bit overlaping it to be clicked add (x,y,width,height) of that location
        self.oneClick = oneClick # can only be cliked down for one frame
        self.DefocusClick = DefocusClick # once clicked it cant be unclicked intel the mouse is not down 
        self.imageLocate = imageLocate # were the image is stored 
        self.text = text # the text displayed on the button
        self.outline = outline # if the button has an outline
        self.background = background #if the button have a background
        self.clickShrink = clickShrink # if the button srinks on click
        self.hoverGrow = hoverGrow # if the button srinks while beeing hovered over
        self.shape = shape # the shape of the button (rectangle, circle)
        self.fontType = fontType
        if ".ttf" in fontType:
            self.importedfont = True 
        else:
            self.importedfont = False
        self.outlineColor = outlineColor
        self.textColor = textColor
        self.backgroundColor = backgroundColor
        self.transparency = transparency
        self.oldEffects = None
        self.oldMods = None
        self.complexColision = complexColision #square collision or not
        self.mask = None #the collision mask
        self.getWidthHeight(width,height)
        createGroupSerface(group)
        self.loadGuiToSurface()
        

    def getWidthHeight(self,width,height): # get the width and height for the button
        if width == None:
            if self.imageLocate == None:
                self.width = 100
                self.height = 100
            else:
                self.width, self.height = self.image.size
        else:
            self.width = width 
            self.height = height
            

    def loadGuiToSurface(self):
        global hasUpdated
        createGroupSerface(self.group)
        self.getImage()
        self.hasUpdated = True
        hasUpdated[self.group] = True
        self.Surface = groupSurfaces[self.group][0].subsurface((self.x-groupSurfaces[self.group][1],self.y-groupSurfaces[self.group][2],self.width, self.height))
        self.Surface.convert_alpha()
        if self.background:
            if self.shape == "rectangle":
                pygame.draw.rect(self.Surface,self.backgroundColor,((0),0,self.width, self.height))
            if self.shape == "circle":
                self.complexColision = True
                if self.width <self.height:
                    radius = int(self.width/2)
                else:
                    radius = int(self.height/2)
                
                pygame.draw.circle(self.Surface,self.backgroundColor,(int(self.width/2),int(self.height/2)),radius)
        if self.imageLocate != None:
            if self.outline:
                self.image = pygame.transform.scale(self.image,(self.width-getOutlineWidth(self.width,self.height)*2,self.height-getOutlineWidth(self.width,self.height)*2)) #when the width and height has been determend scale the image to it
                self.Surface.blit(self.image,(getOutlineWidth(self.width,self.height),getOutlineWidth(self.width,self.height)))
            else:
                self.image = pygame.transform.scale(self.image,(self.width,self.height))
                self.Surface.blit(self.image,(0,0))
            
        if self.outline:
            outlineWidth = getOutlineWidth(self.width,self.height)
            if outlineWidth == 0:
                outlineWidth = 1
            if self.shape == "rectangle":
                pygame.draw.rect(self.Surface,self.outlineColor,(0,0,self.width, self.height),outlineWidth)
            if self.shape == "circle":
                if self.width <self.height:
                    radius = int(self.width/2)
                else:
                    radius = int(self.height/2)
                pygame.draw.circle(self.Surface,self.outlineColor,(int(self.width/2),int(self.height/2)),radius,outlineWidth)
        if self.text != None:             
            self.font,text = getLargetsFont(self.height,self.fontType,self.importedfont,self.width,self.text,self.textColor)

            self.Surface.blit(text,((self.width-text.get_width())/2,(self.height-text.get_height())/2)) # load it on to the surface
        self.mask = pygame.mask.from_surface(self.Surface)
        
            
    def getImage(self): # get the image of the button
        if self.imageLocate != None:
            self.image = pygame.image.load(self.imageLocate)
            

    def checkMouse(self): # see the intaction with the mouse
        ofsetX, ofsetY = mouseX-(self.x+self.xOfset-self.renderdOfsetX), mouseY-(self.y+self.yOfset-self.renderdOfsetY)
        
        if ofsetX > 0 and ofsetY > 0 and ofsetX < self.width and ofsetY < self.height :
            if self.complexColision:
                self.colided = (self.mask).overlap(mouseColison,(ofsetX, ofsetY))
            else:
                self.colided = True
        else:
            self.colided = False
        if self.ExtraClickLocation and self.colided:
            if not(self.ExtraClickLocation[0]<mouseX <self.ExtraClickLocation[0]+self.ExtraClickLocation[2] and self.ExtraClickLocation[1]<mouseY <self.ExtraClickLocation[1]+self.ExtraClickLocation[3]):
                self.colided = False
        if self.colided and mouseOldButtons == (0,0,0):
            self.selected = True
        if self.selected and not(self.colided):
            self.selected = False
        if self.oneClick :
            if self.selected and mouseButtons == (1,0,0) and mouseOldButtons == (0,0,0):
                self.click = True
            else:
                self.click = False
        elif self.selected  and mouseButtons == (1,0,0):
            
            self.click = True
        else:
            if not self.DefocusClick:
                self.click = False
            elif mouseOldButtons == (0,0,0): 
                self.click = False
    
    def transformOnInteract(self): # change the width and height of the button when interacted
        if self.hoverGrow and not(self.click) and self.selected:
            self.xOfset = -int(self.width*0.01) 
            self.yOfset = -int(self.width*0.01)
            if self.xOfset < 1:
                self.xOfset = -1
            if self.yOfset < 1:
                self.yOfset = -1
            self.widthMultiplyer = 1.02
            self.heightMultiplyer = 1.02
            
        elif self.clickShrink and self.click:
            self.xOfset = int(self.width*0.0275) 
            self.yOfset = int(self.width*0.0275)
            if self.xOfset < 2:
                self.xOfset = 2
            if self.yOfset < 2:
                self.yOfset = 2
            self.widthMultiplyer = 0.945
            self.heightMultiplyer = 0.945
            
        else:
            self.xOfset = 0
            self.yOfset = 0
            self.widthMultiplyer = 1
            self.heightMultiplyer = 1

    def checkVisualUpdate(self):
        global hasUpdated
        if self.oldEffects != [self.x,self.y,self.width,self.height,self.xOfset,self.yOfset,self.Surface,self.renderdOfsetY,self.renderdOfsetX,self.transparency] : # check visual changing veriables to see if there was a visual update
            hasUpdated[self.group] = True
        if [self.transparency, self.widthMultiplyer, self.heightMultiplyer, self.rotation] != self.oldMods:
            self.hasUpdated = True
        self.oldEffects = [self.x,self.y,self.width,self.height,self.xOfset,self.yOfset,self.Surface,self.renderdOfsetY,self.renderdOfsetX,self.transparency,self.rotation] # upadte the old visual veriables 
        self.oldMods = [self.transparency, self.widthMultiplyer, self.heightMultiplyer, self.rotation]
    def update(self):
        try:
            self.checkMouse() # update the colison with the mouse
            self.transformOnInteract() # change the look of the button when interacted with
            self.checkVisualUpdate() # sees if it needs to update the buttons visual effects
            
        except : # dose not carsh if theres a error
            pass


    def updateRender(self): # update the look of the button if somthing about it has changed 
        if self.widthMultiplyer != 1 and self.heightMultiplyer !=1: # scale the surface depending on the scale modifiers     
            self.renderSurface = pygame.transform.smoothscale(self.Surface,(int(self.width*self.widthMultiplyer), int(self.height*self.heightMultiplyer)))
        else:
            self.renderSurface = self.Surface
        if self.rotation !=0:
            self.renderSurface = pygame.transform.rotate(self.renderSurface,self.rotation) # roate the button to the chosen roation
        self.renderSurface.set_alpha(self.transparency)


    def render(self,win):   
        if self.hasUpdated: # if somthing has changed update other wise just blit the surface again
            self.hasUpdated = False
            self.updateRender()
        win.blit(self.renderSurface,((self.x+self.xOfset),(self.y+self.yOfset)),) # render the button on to its ui surface

class scrollingBox():
    def __init__(self,group, x,y,width,height,visable=True,renderGroup = None,background = True,backgroundColor = backgroundColor,outline = True,outlineColor = outlineColor,transparency = 255):
        global allGui, hasUpdated
        self.group = group
        self.renderGroup = renderGroup
        self.hasUpdated = True
        hasUpdated[self.group] = True
        hasUpdated[self.group] = True
        self.visable = visable
        self.x =x
        self.y = y
        self.scrolledX = 0
        self.scrolledY = 0
        self.slidedPercentX = 0
        self.slidedPercentY = 0
        self.width = width
        self.height = height
        self.background = background
        self.backgroundColor = backgroundColor
        self.outline = outline
        self.outlineColor = outlineColor
        self.loadBackground()
        self.transparency = transparency
        allGui.append(self)
        self.oldOfsets = [0,0]
        self.oldScroll = [self.slidedPercentX,self.slidedPercentY]
        self.oldWdithHeight = [groupSurfaces[self.renderGroup][0].get_width(),groupSurfaces[self.renderGroup][0].get_height(),self.width,self.height]
        self.renderGroupSurface = pygame.Surface((self.width - getOutlineWidth(self.width,self.height)*2, self.height- getOutlineWidth(self.width,self.height)*2),pygame.HWSURFACE | pygame.DOUBLEBUF| pygame.SRCALPHA)
        if groupSurfaces[self.renderGroup][0].get_width() > self.width:
            buttonWidth = round((self.width/groupSurfaces[self.renderGroup][0].get_width())*self.width )
            self.sliderX = button(self.group, self.x,(self.y+self.height)-getOutlineWidth(self.width,self.height)-10,buttonWidth,getOutlineWidth(self.width,self.height)+10,DefocusClick=True,clickShrink=False)
        if groupSurfaces[self.renderGroup][0].get_height() > self.height:
            buttonHeight = round((self.height/groupSurfaces[self.renderGroup][0].get_height())*self.height )
            self.sliderY = button(self.group, (self.x+self.width)-getOutlineWidth(self.width,self.height)-10,self.y,getOutlineWidth(self.width,self.height)+10,buttonHeight,DefocusClick=True,clickShrink=False)
        createGroupSerface(group)
    def updateButtonWidthHeight(self):
        self.loadBackground()
        try:
            self.sliderX.width = round((self.height/groupSurfaces[self.renderGroup][0].get_height())*self.height )
        except:
            if groupSurfaces[self.renderGroup][0].get_width() > self.width:
                buttonWidth = round((self.width/groupSurfaces[self.renderGroup][0].get_width())*self.width )
                self.sliderX = button(self.group, self.x,(self.y+self.height)-getOutlineWidth(self.width,self.height)-10,buttonWidth,getOutlineWidth(self.width,self.height)+10,DefocusClick=True,clickShrink=False)
        try:
            self.sliderY.height = round((self.height/groupSurfaces[self.renderGroup][0].get_height())*self.height )
        except:
            if groupSurfaces[self.renderGroup][0].get_height() > self.height:
                buttonHeight = round((self.height/groupSurfaces[self.renderGroup][0].get_height())*self.height )
                self.sliderY = button(self.group, (self.x+self.width)-getOutlineWidth(self.width,self.height)-10,self.y,getOutlineWidth(self.width,self.height)+10,buttonHeight,DefocusClick=True,clickShrink=False)
    def loadBackground(self):
        self.backgroundSurface = pygame.Surface((self.width, self.height),pygame.HWSURFACE | pygame.DOUBLEBUF| pygame.SRCALPHA)
        if self.background:
            self.backgroundSurface.fill(self.backgroundColor)
        if self.outline:
            pygame.draw.rect(self.backgroundSurface,self.outlineColor,(0,0,self.width,self.height),getOutlineWidth(self.width,self.height))
    def update(self):
        global hasUpdated
        try:
            if self.sliderX.click:
                self.sliderX.transparency = 255
                if self.x <= mouseX - int(self.sliderX.width/2) <= self.x + self.width - self.sliderX.width:
                    self.sliderX.x = mouseX - int(self.sliderX.width/2)
                    self.slidedPercentX = (self.sliderX.x - self.x)/(self.width - self.sliderX.width)
                elif self.x <= mouseX - int(self.sliderX.width/2): 
                    self.sliderX.x = self.x + self.width - self.sliderX.width
                    self.slidedPercentX = (self.sliderX.x - self.x)/(self.width - self.sliderX.width)
                else:
                    self.sliderX.x = self.x
                    self.slidedPercentX = (self.sliderX.x - self.x)/(self.width - self.sliderX.width)     
            else:
                self.sliderX.transparency = 100
                self.sliderX.hasUpdated = True
        except:
            pass
        try:    
            if self.sliderY.click:
                self.sliderY.transparency = 255
                if self.y <= mouseY - int(self.sliderY.height/2) <= self.y + self.height - self.sliderY.height:
                    self.sliderY.y = mouseY - int(self.sliderY.height/2)
                    self.slidedPercentY = (self.sliderY.y - self.y)/(self.height - self.sliderY.width)
                elif self.y <= mouseY - int(self.sliderY.height/2): 
                    self.sliderY.y = self.y + self.height - self.sliderY.height
                    self.slidedPercentY = (self.sliderY.y - self.y)/(self.height - self.sliderY.height)
                else:
                    self.sliderY.y = self.y
                    self.slidedPercentY = (self.sliderY.y - self.y)/(self.height - self.sliderY.height) 
            else:
                self.sliderY.transparency = 100
                self.sliderY.hasUpdated = True
        except:
            pass
        try:
            if  self.x<mouseX <self.x+self.width and self.y <mouseY <self.y+self.height:
                for event in events:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 4 and self.y <= self.sliderY.y - round(self.height /30)<= self.y + self.height - self.sliderY.height:
                                self.sliderY.y -= round(self.height /30)
                                self.slidedPercentY = (self.sliderY.y - self.y)/(self.height - self.sliderY.height)
                            elif event.button == 5 and self.y <= self.sliderY.y + round(self.height /30) <= self.y + self.height - self.sliderY.height:
                                self.sliderY.y += round(self.height /30)
                                self.slidedPercentY = (self.sliderY.y - self.y)/(self.height - self.sliderY.height)
                            elif event.button == 5 and self.y <= self.sliderY.y - round(self.height /30): 
                                self.sliderY.y = self.y + self.height - self.sliderY.height
                                self.slidedPercentY = (self.sliderY.y - self.y)/(self.height - self.sliderY.height)
                            elif event.button == 4:
                                self.sliderY.y = self.y
                                self.slidedPercentY = (self.sliderY.y - self.y)/(self.height - self.sliderY.height) 
        except:
            pass
        if self.oldScroll != [self.slidedPercentX,self.slidedPercentY]:
            self.hasUpdated = True
            hasUpdated[self.group] = True
            
        self.oldScroll = [self.slidedPercentX,self.slidedPercentY]
        if self.oldWdithHeight != [groupSurfaces[self.renderGroup][0].get_width(),groupSurfaces[self.renderGroup][0].get_height(),self.width,self.height]:
            self.hasUpdated = True
            hasUpdated[self.group] = True
            self.updateButtonWidthHeight()
            
        self.oldWdithHeight = [groupSurfaces[self.renderGroup][0].get_width(),groupSurfaces[self.renderGroup][0].get_height(),self.width,self.height]
        
    def updateRender(self):
        global hasUpdated
        if round(groupSurfaces[self.renderGroup][0].get_width()-(self.renderGroupSurface.get_width()),0)>0:
            xOfset = round(self.slidedPercentX *(groupSurfaces[self.renderGroup][0].get_width()-(self.renderGroupSurface.get_width())+20),0)
        else:
            xOfset = 0
        if round((groupSurfaces[self.renderGroup][0].get_height()-(self.height - (getOutlineWidth(self.width,self.height)*2))),0)>0:
            yOfset = round(self.slidedPercentY *(groupSurfaces[self.renderGroup][0].get_height()-(self.renderGroupSurface.get_height())+20),0)
        else:
            yOfset = 0 
        
        if self.oldOfsets != [xOfset,yOfset]:
            hasUpdated[self.group] = True
        for part in allGui: # make sure the gui on the surface knows where it is on the screen to be able to colid with the mouse 
            if part.group == self.renderGroup:
                part.ExtraClickLocation =(self.x,self.y,self.width,self.height)
                part.renderdOfsetX = -self.x #+ xOfset
                part.renderdOfsetY = -self.y #+ yOfset
                if self.oldOfsets != [xOfset,yOfset]:
                    part.x -= round(xOfset - self.oldOfsets[0])
                    part.y -= round(yOfset - self.oldOfsets[1])
                
        self.oldOfsets = [xOfset,yOfset]
        if self.renderGroup in hasUpdated:
            self.renderGroupSurface.fill((0,0,0,0))
            displayGui(self.renderGroupSurface,self.renderGroup)
            
    def render(self,win):
        if self.hasUpdated or self.renderGroup in hasUpdated: # if somthing has changed update other wise just blit the surface again
            self.hasUpdated = False
            self.updateRender()
        win.blit(self.backgroundSurface,(self.x,self.y))
        win.blit(self.renderGroupSurface,(self.x+getOutlineWidth(self.width,self.height),self.y+getOutlineWidth(self.width,self.height)))

class textBox():
    def __init__(self,group, x,y,width,height,visable=True,text = "",maxLines = 1000,textColor = textColor,splitWords = True, backgroundColor = backgroundColor,outline = True,outlineColor = outlineColor , fontType = font,editable = True,xAlinment = 1,yAlinment = 1,filter = "",transparency = 255):
        global allGui, hasUpdated
        self.group = group #the name of the group for the text box to be used in
        self.hasUpdated = True
        self.textUpdate = True
        hasUpdated[self.group] = True#update the things in the group that the text box will be rendered to 
        self.visable = True
        self.x = x #set the x,y, width, height of the text box to what the user inputed when stating the class
        self.y = y
        self.width = width 
        self.height = height
        self.text = text
        self.splitWords = splitWords #if words get spit at the end of lines (lags alot with long word atm)
        self.transparency = transparency#how transparent the text box is
        self.textColor = textColor
        self.textLines = 1
        self.maxLines = maxLines
        self.selected = False
        self.toggleCursor = False
        self.cursorLocation = None
        self.dt = time.time()
        self.filter = filter
        self.outline = outline
        self.backgroundColor = backgroundColor
        self.fontType = fontType
        if ".ttf" in self.fontType:
            self.importedfont = True
        else:
            self.importedfont = False
        self.chachedFonts = {}
        self.editable = editable
        self.currentPressed = None # a variable to store the current pressed key to be repeated multiple times
        self.currentPressedDelay = 0.5 # adds a delay before spaming a key 
        self.keyStartTime = time.time()
        self.oldText = ""
        self.oldVars = [self.x,self.y,self.width,self.height,self.group]
        self.xAlinment = xAlinment #the text alinment in the box 1 = left 2 = middle 3 = right
        self.yAlinment = yAlinment #the text alinment in the box 1 = top 2 = middle 3 = bottom
        self.textSurface = pygame.Surface((self.width, self.height),pygame.HWSURFACE | pygame.DOUBLEBUF| pygame.SRCALPHA)#create a surface to render the final text to 
        self.outlineColor = outlineColor
        self.background = button(self.group,self.x,self.y,self.width,self.height,self.visable,hoverGrow=False,clickShrink=False,transparency = transparency,backgroundColor=self.backgroundColor,oneClick=True,outline=outline,outlineColor=outlineColor) # create a button to use as the background and to workout when it is clicked
        allGui.append(self)
        self.getTextHeight()
        self.loadTextToLines(False) # load the current text to lines so it fits in the box


    def getTextHeight(self): # get the height of the text to make it fit on to the lines needed 
        if self.outline: # if the text box has an outline subtract that from the avalible space to create the text
            textHeight = self.height - (getOutlineWidth(self.width,self.height)/2)
        else: 
            textHeight = self.height

        fontHeight = textHeight/self.textLines
        self.font,test = getLargetsFont(fontHeight,self.fontType,self.importedfont)
        

    def loadTextToLines(self,looped): #work out the needed lines then seperate the text on to them 
        self.textLined = []
        self.getTextLinesNeeded(self.textLines)# get the amount of lines needed to render the text 
        boxWidth =  self.width - getOutlineWidth(self.width,self.height)*2 # get the width avalible to render the text to 
        if not(self.splitWords):
            currentLetter = 0 # creat a var to keep track of what text needs to be rended
            for letter in range(0,len(self.text)+1): # start a loop to go through evey letter in the text box
                line = self.text[currentLetter:letter] # create the line that could be rendered next
                nextLine = self.text[currentLetter:letter+1] # create the line that would be the one after the next one
                if self.font.render(line, 1, self.textColor).get_width() <= boxWidth < self.font.render(nextLine, 1, self.textColor).get_width() or "\n" in line:#if the line fits but is not to short render it. or if there is an enter
                    currentLetter = letter
                    self.textLined.append(self.font.render(line.replace("\n",""), 1, self.textColor))
                elif letter >= len(self.text): # if its the last bit of the text render it how ever long it is
                    self.textLined.append(self.font.render(line.replace("\n",""), 1, self.textColor))
        else:
            words = self.text.split(" ")
            currentword = 0 # creat a var to keep track of what text needs to be rended
            for word in range(0,len(words)+1): # start a loop to go through evey word in the text box
                line = words[currentword:word] # create the line that could be rendered next
                line = " ".join(str(part)for part in line)
                nextLine = words[currentword:word+1] # create the line that would be the one after the next one
                nextLine = " ".join(str(part)for part in nextLine)
                if self.font.render(line, 1, self.textColor).get_width() <= boxWidth < self.font.render(nextLine, 1, self.textColor).get_width() or "\n" in line:#if the line fits but is not to short render it. or if there is an enter
                    currentword = word
                    self.textLined.append(self.font.render(line.replace("\n",""), 1, self.textColor))
                elif word >= len(words): # if its the last bit of the text render it how ever long it is
                    self.textLined.append(self.font.render(line.replace("\n",""), 1, self.textColor))
        if "\n" == self.text[-1:] and line != "\n":#if the is an enter at the end of the text still add a new line
           self.textLined.append(self.font.render("", 1, self.textColor))

        temp = self.textLined  # flip the list to make it the right way around
        self.textLined = []
        if self.maxLines: # clamp the line to the max lines
            for value in range(len(temp)-1,max(len(temp)-self.maxLines-1,-1),-1):
                self.textLined.append(temp[value])
        else:
            for value in range(len(temp)-1,-1,-1):
                self.textLined.append(temp[value])
        if self.textLined == []:
            self.textLined = [self.font.render("", 1, self.textColor)]
        if min(self.maxLines-1,len(self.textLined))<self.textLines and not(looped):#if there is less lines rendered than can fit cheach to see if the text can be bigger
            self.textLines = 1 
            self.getTextLinesNeeded(1)
            self.loadTextToLines(True)
        self.textLines = len(self.textLined)

    def getTextLinesNeeded(self,Lines): # get the amount of lines needed to render text 
        self.getTextHeight()        
        #get the length of the text box
        boxWidth =  self.width - getOutlineWidth(self.width,self.height)*2
        textSpace = boxWidth * (Lines -0.1 )
        if "\n" in self.text:
            for i in range(0,len(self.text)+1):
                if self.text[i:i+1] == "\n":
                    Lines += 1
        #get the length of the whole text
        if self.splitWords:
            longestWord = 0
            for word in self.text.split(" "):
                if len(word) > longestWord:
                    longestWord = len(word)
            extraSpace = " " * (Lines * round(longestWord))
            allText = self.font.render(self.text.replace("\n","")+extraSpace, 1, self.textColor) 
        else:
            allText = self.font.render(self.text.replace("\n",""), 1, self.textColor)    
        textWidth= allText.get_width()  
        if textSpace >textWidth: # it with the lines the text fits return true
            return True
        elif self.textLines < self.maxLines: # else incrase the lines to so if text fits
            self.textLines +=1
            return self.getTextLinesNeeded(self.textLines)
    
    def addText(self): # add text from keybord input
        global hasUpdated
        for event in events:
            if event.type == pygame.KEYDOWN  :# see if a key is pressed
                if event.key == pygame.K_RETURN: # add a new line when enters pressed
                    self.currentPressed= "\n"
                    self.text += self.currentPressed
                    self.keyStartTime = time.time()
                elif event.key == pygame.K_BACKSPACE: # delete a letter if backspace is pressed
                    self.currentPressed= -1
                    self.text = self.text[:-1]
                    self.keyStartTime = time.time()
                elif event.key == pygame.K_ESCAPE: # leave the box if escape is presed
                    self.selected = False
                    self.hasUpdated
                    self.textUpdate
                    hasUpdated[self.group] = True
                    self.toggleCursor = False
                else:
                    if self.filter == "" or event.unicode in self.filter:
                        self.currentPressed=event.unicode# add the text to the box when text is presed
                        self.text += self.currentPressed
                        self.keyStartTime = time.time()

            elif event.type == pygame.KEYUP  :# see if a key is pressed
                if event.key == pygame.K_RETURN and self.currentPressed =="\n": # add a new line when enters pressed
                    self.currentPressed= None
                elif event.key == pygame.K_BACKSPACE and self.currentPressed == -1: # delete a letter if backspace is pressed
                    self.currentPressed= None
                elif self.filter == "" or event.unicode in self.filter and self.currentPressed == event.unicode :
                        self.currentPressed= None# add the text to the box when text is presed:

        if self.currentPressed != None and time.time()-self.keyStartTime >self.currentPressedDelay:
            if self.currentPressed == -1 :
                self.text = self.text[:-1]
            else:
                self.text += self.currentPressed
                

    def toggleSelected(self): # toggle wether the the text box is selected
        global hasUpdated
        if self.background.click:
            self.selected = not(self.selected) # switch the variable
            self.toggleCursor = False
            self.hasUpdated = True
            hasUpdated[self.group] = True
        if not(self.background.selected) and mouseButtons == (1,0,0) and self.selected: # if clicked of the box is un selected 
            self.selected = False
            self.toggleCursor = False
            self.hasUpdated = True
            hasUpdated[self.group] = True

    def toggleCursors(self):
        global hasUpdated
        if time.time() -self.dt > 1:
            self.toggleCursor = not(self.toggleCursor)
            self.dt = time.time()
            self.hasUpdated = True
            hasUpdated[self.group] = True
    

    def update(self): # update if selected then the text input
        global hasUpdated
        self.toggleSelected()
        if self.text != self.oldText:
            self.hasUpdated = True
            self.textUpdate = True
            hasUpdated[self.group] = True
        if self.selected and self.editable:
            self.addText()
            self.toggleCursors()
            if self.background.hasUpdated:
                self.hasUpdated = True
                hasUpdated[self.group] = True         
        if self.oldVars != [self.x,self.y,self.width,self.height,self.group,self.transparency]:
            self.hasUpdated = True
            hasUpdated[self.group] = True   
        self.oldVars = [self.x,self.y,self.width,self.height,self.group,self.transparency]
    def updateRender(self):
        
        if self.textUpdate:
            self.textUpdate = False
            self.textSurface.fill((0,0,0,0))
            self.loadTextToLines(False) # split the text on to lines
            for text in self.textLined[::-1]: # render the text to the box 
                if self.xAlinment == 1:
                    if self.outline:
                        alinedX = int(getOutlineWidth(self.width,self.height))
                    else:
                        alinedX = 0
                elif self.xAlinment == 2:
                    alinedX = (self.width-text.get_width())/2 # get the text to the middle of the box 
                elif self.xAlinment ==3:
                    alinedX = (self.width-text.get_width())
                if self.yAlinment == 1:
                    if self.outline:
                        alinedY = round(getOutlineWidth(self.width,self.height),0)
                    else:
                        alinedY = 0
                elif self.yAlinment == 2:
                    alinedY = (self.height-(text.get_height()*self.textLines))/2 
                elif self.yAlinment == 3:
                    alinedY = (self.height-(text.get_height()*self.textLines))
                self.textSurface.blit(text,((alinedX,alinedY +round(text.get_height()*self.textLined[::-1].index(text),0)))) # render the text on top of the background 
                self.cursorLocation = [alinedX+self.textLined[0].get_width(),alinedY+round(self.textLined[0].get_height()*(self.textLines-1),0),self.textLined[0].get_height()]
        if self.selected and self.toggleCursor:
            pygame.draw.rect(self.textSurface,self.textColor,(self.cursorLocation[0],self.cursorLocation[1],2,self.cursorLocation[2]))
        else:
            pygame.draw.rect(self.textSurface,(0,0,0,0),(self.cursorLocation[0],self.cursorLocation[1],2,self.cursorLocation[2]))
        self.textSurface.set_alpha(self.transparency)
        #update the background        
        self.updateBackground()
        
        self.oldText = self.text
    def updateBackground(self):
        self.background.group = self.group
        self.background.x = self.x
        self.background.y = self.y
        self.background.transparency = self.transparency
        self.background.width = self.width
        self.background.height = self.height
        self.background.backgroundColor = self.backgroundColor
        self.background.loadGuiToSurface()
        self.background.hasUpdated = True
    def render(self,win): # render the text box to the screen 
        if self.hasUpdated: # if somthing has changed update other wise just blit the surface again
            self.hasUpdated = False
            self.updateRender()
        win.blit(self.textSurface,(self.x,self.y))
        

class slider():
    def __init__(self,group, x,y,width,height,visable=True,background = True,backgroundColor = backgroundColor,outline = True,outlineColor = outlineColor,transparency = 255,text = None,fontType = font,textColor = textColor,slideable= True,statingPercentage =0):
        global allGui, hasUpdated
        allGui.append(self)
        self.group = group
        self.hasUpdated = True        
        hasUpdated[self.group] = True
        self.visable = visable
        self.x =x
        self.y = y 
        self.height =height
        self.width = width 
        self.text = text  
        self.textColor = textColor
        self.outline = outline
        self.outlineColor = outlineColor
        self.backgroundColor =backgroundColor
        self.oldVars = None
        self.background = background
        self.fontType = fontType
        if ".ttf" in fontType:
            self.importedfont = True
        else:
            self.importedfont = False
        self.renderdOfsetX =  0 # render of set to use for the buttons hit box 
        self.renderdOfsetY = 0 
        self.slideable = slideable # if false the slide bar will no move
        self.slider = None
        self.slidedPercent = statingPercentage          
        createGroupSerface(group)
        
        self.loadGuiToSurface()
        
    
            
        
        
    def loadGuiToSurface(self):
        
        self.Surface = groupSurfaces[self.group][0].subsurface((self.x-groupSurfaces[self.group][1],self.y-groupSurfaces[self.group][2],self.width, self.height))
            
        self.Surface.fill((0,0,0,0))
        if self.text != None:
            self.scrollHeight = int(self.height / 2)
        else:
            self.scrollHeight = self.height
        if self.background:
                pygame.draw.rect(self.Surface,self.backgroundColor,(0,self.height-self.scrollHeight,self.width, self.scrollHeight),border_radius =int(self.scrollHeight/2 ))
        if self.outline:
            outlineWidth = int(getOutlineWidth(self.width,self.height))
            if outlineWidth == 0:
                outlineWidth = 1
            
            pygame.draw.rect(self.Surface,self.outlineColor,(0,self.height-self.scrollHeight,self.width, self.scrollHeight),outlineWidth,border_radius =int(self.scrollHeight/2))
        self.CreateSlider()
        if self.text != None: 
            font,text = getLargetsFont(self.scrollHeight,self.fontType,self.importedfont,self.width,self.text,self.textColor)
            
            self.Surface.blit(text,((int(self.width-text.get_width())/2),0)) # load it on to the surface 
        
    def CreateSlider(self):
        if self.slider == None:
            self.slider = button(self.group,self.x,(self.y + (self.height-self.scrollHeight)),self.scrollHeight,self.scrollHeight,shape="circle",background=self.backgroundColor,outlineColor = self.outlineColor,hoverGrow=False,DefocusClick=True)
            if self.slideable:
                self.slider.visable = True
                self.slider.x =self.x+int((self.width- self.slider.width )*self.slidedPercent)
            
            else:
                self.slider.visable = False
            self.slider.renderdOfsetX   = self.renderdOfsetX  
            self.slider.renderdOfsetY   = self.renderdOfsetY
    def update(self):
        if self.oldVars != [self.text,self.textColor,self.width,self.height,self.background,self.backgroundColor,self.fontType]: # check if all the defining visual vars are the same and if it needs to update its visual output
            global hasUpdated
            self.hasUpdated = True
            hasUpdated[self.group] = True       
        self.oldVars = [self.text,self.textColor,self.width,self.height,self.background,self.backgroundColor,self.fontType]
        if self.slider.click and self.slideable:
            if self.x <= (mouseX + self.renderdOfsetX  ) - int(self.slider.width/2) <= self.x + self.width - self.slider.width:
                self.slider.x = (mouseX + self.renderdOfsetX  ) - int(self.slider.width/2)
                self.slidedPercent = (self.slider.x - self.x)/(self.width - self.slider.width)
            elif self.x <= (mouseX + self.renderdOfsetX  ) - int(self.slider.width/2): 
                self.slider.x = self.x + self.width - self.slider.width
                self.slidedPercent = (self.slider.x - self.x)/(self.width - self.slider.width)
            else:
                self.slider.x = self.x
                self.slidedPercent = (self.slider.x - self.x)/(self.width - self.slider.width)
    def render(self,win):
        if self.hasUpdated:
            self.loadGuiToSurface()            
            self.hasUpdated = False  
                  
            
        win.blit(self.Surface,((self.x),(self.y)))
        



class FPSCounter():
    def __init__(self,textColor = pygame.Color("coral"),font = font,fontSize = "22"):
        self.textColor = textColor
        self.font = font
        self.fontSize = fontSize
        self.clock = pygame.time.Clock()
        self.renderFont = pygame.font.SysFont(self.font,int(self.fontSize))
    def render(self,win,fpsCap = 0):
        dt = self.clock.tick(fpsCap)
        self.fps = str(int(self.clock.get_fps()))
        fps_text = self.renderFont.render(self.fps, 1, self.textColor)
        win.blit(fps_text,(0,0))
    def cap(self,fpsCap):
        dt = self.clock.tick(fpsCap)
        



        
        


