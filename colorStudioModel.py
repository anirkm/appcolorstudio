# -*- coding: utf-8 -*-
"""
Color Studio - Rémi Cozot 2019
Auteurs: KARAMI Anir, ARABAH Yanis (BUT3 INFO - APP Parcours A - 2026)
----------------------------------
new version of 
Color Studio - Rémi Cozot 2019
"""

# ----------------------------------------------------------------------------------
# import(s)
# ----------------------------------------------------------------------------------

from colorStudioUtils import loadImage, printProgressBar, image2Ymean

import math
import numpy as np
import skimage

import xml.dom.minidom as miniXml

# ----------------------------------------------------------------------------------
# Class(es)
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
#  IMAGES
# ----------------------------------------------------------------------------------
class Images:
    """
    set of images 
    """
    def __init__(self,pathImage,baseImageName,extImageName,nbImage,nbDigit,load=True, scale = 0.5):

        # path to images data
        self._pathImage = pathImage
        self._baseImageName = baseImageName
        self._extImageName = extImageName
        self._nbImage = nbImage
        self._nbDigit = nbDigit
        # list of images
        self._images = []

        if load:  self.loadImages(scale)

    def loadImages(self, scale =0.5):
        for i in range(self._nbImage):
            printProgressBar (i, self._nbImage-1, prefix = '', suffix = '', decimals = 1, length = 50, fill = '█')

            # create formated filename
            iStr = str(i).zfill(self._nbDigit)
            name =  self._pathImage+self._baseImageName+iStr+self._extImageName

            # load image
            img = loadImage(name, scale)

            self._images.append(img)

    def clear(self): self._images.clear()

    def len(self): return self._nbImage
# ----------------------------------------------------------------------------------
#  LIGHT
# ----------------------------------------------------------------------------------
class Light:
    # class attribute
	lightNb = 0
	
	def __init__(self,name=None):
		if not name:	
			self._name = "Light"+str(Light.lightNb)
		else:
			self._name = name
	
		Light.lightNb = Light.lightNb+1
		
		# light color
		self._npColorRGB = np.asarray([1.0,1.0,1.0])
		
		# exposure 
		self._exposure = 0
		
		# light orientation and idx
		self._imageIdx = 0
		self._maxIdx = 0
		
		# ref to render images
		self._ImagesArray = None
		
		# optimization
		self._needUpdate = False
		self._firstUpdate = True
		
		self._currentImage = None

	def setImagesArray(self, imgArray):
		self._ImagesArray = imgArray
		self._maxIdx = self._ImagesArray.len()
	
	def clear(self): self._ImagesArray.clear()
		
	def setExposure(self,expValue):
		self._exposure = expValue
		self._needUpdate = True

	def setColor(self,color):
		self._npColorRGB = color
		self._needUpdate = True
	
	def setImageIdx(self,idx):
		self._imageIdx = idx
		self._needUpdate = True
	
	def render(self):
		if self._firstUpdate or self._needUpdate:
			# get current active image
			img = self._ImagesArray._images[self._imageIdx]
			# Vectorised color filter and exposure
			imgOut = img * self._npColorRGB * (2.0 ** self._exposure)
			self._currentImage = imgOut
			self._firstUpdate = False
			self._needUpdate = False
		else:
			imgOut = self._currentImage
		return imgOut
	
	def print(self):
		print("[ Light:",self._name, ",",                   \
			"imgIdx:",self._imageIdx,"/",self._maxIdx,",",  \
			"exposure:",self._exposure,                     \
			"color:","[ r:",self._npColorRGB[0],", g:",self._npColorRGB[1],",b:",self._npColorRGB[2],"]",   \
		"]")

	def toXML(self):
		
		lightMark = "LIGHT"
		inputFileMark = "INPUTFILE"
		idxPosMark = "IDXPOS"
		expMark = "EXP"
		colorMark ="COLOR"
		rMark = "R"
		gMark ="G"
		bMark = "B"
		
		outString ="<"+lightMark+" name=\""+self._name+"\""+">"+"\n"+ \
			"<"+inputFileMark+ \
			" ext=\"" + \
			self._ImagesArray._extImageName+ \
			"\" min=\"0\" max=\""+str(self._ImagesArray._nbImage)+"\" "+ \
			" digit=\""+ str(self._ImagesArray._nbDigit) + "\" >" + \
			self._ImagesArray._pathImage+self._ImagesArray._baseImageName+ \
			"</"+inputFileMark+">"+"\n"+ \
			"<"+idxPosMark+">"+ str(self._imageIdx)+"</"+idxPosMark+">"+ "\n"+\
			"<"+expMark+">"+str(self._exposure)+"</"+expMark+">"+"\n"+ \
			"<"+colorMark +" format=\"float\""+">"+ "\n" +\
			"<"+rMark+">"+str(self._npColorRGB[0])+"</"+rMark+">"+"\n"+ \
			"<"+gMark+">"+str(self._npColorRGB[1])+"</"+gMark+">"+"\n"+ \
			"<"+bMark+">"+str(self._npColorRGB[2])+"</"+bMark+">"+"\n"+ \
			"</"+colorMark+">"+"\n"+ \
			"</"+lightMark+">"
		return outString

# ----------------------------------------------------------------------------------
#  SCENE
# ----------------------------------------------------------------------------------
class Scene:
    def __init__(self, hdr = False):
        self._lights = []           # set of lights
        self._hdr = hdr
        
        # Standard post-processes in exact pipeline order
        self._whiteBalance = WhiteBalance()
        self._autoExposure = AE_Ymean(Ytarget=0.5, exposure=0.0)
        self._saturation = Saturation()
        self._gamma = Gamma(gamma=1.0)
        
        self._postProcesses = [
            self._whiteBalance,
            self._autoExposure,
            self._saturation,
            self._gamma
        ]

    def addLight(self,light): self._lights.append(light)

    def addPostProcess(self, postProcess): 
        # Avoid duplicate standard post-processes if added manually
        if isinstance(postProcess, WhiteBalance):
            self._postProcesses.remove(self._whiteBalance)
            self._whiteBalance = postProcess
            self._postProcesses.insert(0, self._whiteBalance)
        elif isinstance(postProcess, AE_Ymean):
            self._postProcesses.remove(self._autoExposure)
            self._autoExposure = postProcess
            self._postProcesses.insert(1, self._autoExposure)
        elif isinstance(postProcess, Saturation):
            self._postProcesses.remove(self._saturation)
            self._saturation = postProcess
            self._postProcesses.insert(2, self._saturation)
        elif isinstance(postProcess, Gamma):
            self._postProcesses.remove(self._gamma)
            self._gamma = postProcess
            self._postProcesses.insert(3, self._gamma)
        else:
            self._postProcesses.append(postProcess)

    def clear(self):
        self._lights.clear()
        # Reset standard post-processes to default values
        self._whiteBalance.setColor(np.array([1.0, 1.0, 1.0]))
        self._autoExposure._Ytarget = 0.5
        self._autoExposure.setExposure(0.0)
        self._autoExposure.setOnOff(True)
        self._saturation.setLinearSaturation(0.0)
        self._saturation.setGammaSaturation(0.0)
        self._gamma.setGamma(1.0)

    def getLightByName(self,name):
        returnLight = None
        for light in self._lights :
            if light._name == name :
                returnLight = light
                break
        return returnLight

    def render(self):
        # create image to store render image
        imgOut = np.zeros(self._lights[0]._ImagesArray._images[0].shape)

        # render all lights
        for light in self._lights:
            imgOut = imgOut+light.render()	

        # applyPostProcess
        for pp in self._postProcesses:
            imgOut = pp.postProcess(imgOut)

        if not self._hdr :
            # clipping values
            imgOut = np.clip(imgOut,0.0,1.0)
        return imgOut

    def toXML(self):
        # create XML string
        lsMark = "LIGHTS"
        lightsString = "<"+lsMark+">"+"\n"
        for l in self._lights :
            lightsString = lightsString+l.toXML()+"\n"
        lightsString = lightsString + "</" +lsMark +">"
        
        ppMark = "POSTPROCESSES"
        ppString = "<"+ppMark+">"+"\n"
        for pp in self._postProcesses:
            if hasattr(pp, 'toXML'):
                ppString = ppString+pp.toXML()+"\n"
        ppString = ppString + "</" +ppMark +">"
        
        outString = "<LIGHTSETTUP>\n" + lightsString + "\n" + ppString + "\n</LIGHTSETTUP>\n"
        return outString

    def fromXML(self, xmlFile, scale =0.5):
        # parse XML file
        xdoc = miniXml.parse(xmlFile)

        # recover <LIGHT> tag
        xLights = xdoc.getElementsByTagName('LIGHT')

        # dict {'filename':[light]} to avoid multiple rendered-image file loads
        filenameLight = {}

        # for each light TAG
        for xl in xLights:
            # recover light name
            lightName = xl.attributes['name'].value

            # input file : <INPUTFILE ext=".jpg" min="0" max="100"  digit="4" >./images/set02/arnold_pass</INPUTFILE>
            input = xl.getElementsByTagName('INPUTFILE')[0]
            ext = input.attributes['ext'].value
            min = int(input.attributes['min'].value)
            max = int(input.attributes['max'].value)
            digit = int(input.attributes['digit'].value)
            imagesFile = input.firstChild.data	

            # index light position : <IDXPOS>36</IDXPOS>
            idxPos = int(xl.getElementsByTagName('IDXPOS')[0].firstChild.data)
            
            #exposure : <EXP>0.0</EXP>
            exp = float(xl.getElementsByTagName('EXP')[0].firstChild.data)	

    		# color : <COLOR format="float"> <R>1.0</R> <G>1.0</G> <B>1.0</B> </COLOR>
            color =  xl.getElementsByTagName('COLOR')[0]
            rr =  float(color.getElementsByTagName('R')[0].firstChild.data)
            gg =  float(color.getElementsByTagName('G')[0].firstChild.data)
            bb =  float(color.getElementsByTagName('B')[0].firstChild.data)

            # create light
            light = Light(name=lightName)
            light.setExposure(exp)
            light.setColor(np.asarray([rr,gg,bb]))
            light.setImageIdx(idxPos)
            images = Images('',imagesFile,ext,max,digit,load=False)
            light.setImagesArray(images)

            # add current light to allLights
            self._lights.append(light)

            # filenameLight
            if imagesFile in filenameLight: filenameLight[imagesFile].append(light) # imagesFile already used
            else: filenameLight.update({imagesFile:[light]})

        # recover <POSTPROCESS> tag
        print("<ColorStudio: DEBUG>")
        xPosts = xdoc.getElementsByTagName('POSTPROCESS')

        # explore postprocess
        for xp in xPosts:
            children = xp.childNodes # all children
            for child in children:
                childNodeIsElement = (child.nodeType  == miniXml.Node.ELEMENT_NODE)
                if childNodeIsElement : 
                    # child is ELEMENT
                    if child.tagName == 'CHROMA':
                        # <CHROMA type="AWB"|"SATURATION"|"saturation">
                        typeString = child.attributes['type'].value
                        print('<CHROMA type="',typeString,'">')
                        if typeString=='AWB':
                            color_nodes = child.getElementsByTagName('COLOR')
                            if color_nodes:
                                color = color_nodes[0]
                                r = float(color.getElementsByTagName('R')[0].firstChild.data)
                                g = float(color.getElementsByTagName('G')[0].firstChild.data)
                                b = float(color.getElementsByTagName('B')[0].firstChild.data)
                                self._whiteBalance.setColor(np.array([r, g, b]))
                        elif typeString=='saturation' or typeString=='SATURATION':
                            linear_nodes = child.getElementsByTagName('LINEAR')
                            gamma_nodes = child.getElementsByTagName('GAMMA')
                            linear_val = float(linear_nodes[0].firstChild.data) if linear_nodes else 0.0
                            gamma_val = float(gamma_nodes[0].firstChild.data) if gamma_nodes else 0.0
                            self._saturation.setLinearSaturation(linear_val)
                            self._saturation.setGammaSaturation(gamma_val)

                    elif child.tagName == 'LUMINANCE':
                        # <LUMINANCE type="AE"|"GAMMA">
                        typeString = child.attributes['type'].value
                        print('<LUMINANCE type="',typeString,'">')
                        if typeString=='AE':
                            y_nodes = child.getElementsByTagName('Y')
                            y_val = float(y_nodes[0].firstChild.data) if y_nodes else 0.5
                            self._autoExposure._Ytarget = y_val
                        elif typeString=='GAMMA':
                            gamma_nodes = child.getElementsByTagName('GAMMA')
                            gamma_val = float(gamma_nodes[0].firstChild.data) if gamma_nodes else 1.0
                            self._gamma.setGamma(gamma_val)

        # rendered-image files management
        # just load once rendered-image files
        for k in filenameLight.keys():
            # lights that uses filenameLight
            lights = filenameLight[k]
            firstLight = lights[0] # at least one light uses this rendered-images file set
            # load images
            imgs = Images( 								    \
                firstLight._ImagesArray._pathImage, 		\
                firstLight._ImagesArray._baseImageName, 	\
                firstLight._ImagesArray._extImageName,	    \
                firstLight._ImagesArray._nbImage,			\
                firstLight._ImagesArray._nbDigit,			\
                load=True, scale=scale)
            
            # light share rendered-image files
            for li in lights: li.setImagesArray(imgs)
        



    def print(self):
        print(" -------- LIGHTS -------- ")
        for l in self._lights: l.print()
# ----------------------------------------------------------------------------------
#  POST PROCESS
# ----------------------------------------------------------------------------------
class PostProcess:

	def __init__(self):
		pass

	def postProcess(self,img):
		return img
# ----------------------------------------------------------------------------------
#  POST PROCESS : WHITE BALANCE
# ----------------------------------------------------------------------------------
class WhiteBalance(PostProcess):

    def __init__(self, color=None):
        super().__init__()
        if color is None:
            self._npColorRGB = np.array([1.0, 1.0, 1.0])
        else:
            self._npColorRGB = np.asarray(color)

    def setColor(self, color):
        self._npColorRGB = np.asarray(color)

    def postProcess(self, img):
        return img * self._npColorRGB

    def toXML(self):
        return (
            f'\t\t<POSTPROCESS name="white balance">\n'
            f'\t\t\t<CHROMA type="AWB">\n'
            f'\t\t\t\t<COLOR format="float">\n'
            f'\t\t\t\t\t<R>{self._npColorRGB[0]}</R>\n'
            f'\t\t\t\t\t<G>{self._npColorRGB[1]}</G>\n'
            f'\t\t\t\t\t<B>{self._npColorRGB[2]}</B>\n'
            f'\t\t\t\t</COLOR>\n'
            f'\t\t\t</CHROMA>\n'
            f'\t\t</POSTPROCESS>'
        )
# ----------------------------------------------------------------------------------
#  POST PROCESS : GAMMA
# ----------------------------------------------------------------------------------
class Gamma(PostProcess):

    def __init__(self, gamma=1.0):
        super().__init__()
        self._gamma = gamma

    def setGamma(self, gamma):
        self._gamma = gamma

    def postProcess(self, img):
        if self._gamma != 1.0 and self._gamma > 0.0:
            img_clipped = np.clip(img, 0.0, None)
            return np.power(img_clipped, 1.0 / self._gamma)
        return img

    def toXML(self):
        return (
            f'\t\t<POSTPROCESS name="gamma">\n'
            f'\t\t\t<LUMINANCE type="GAMMA">\n'
            f'\t\t\t\t<GAMMA>{self._gamma}</GAMMA>\n'
            f'\t\t\t</LUMINANCE>\n'
            f'\t\t</POSTPROCESS>'
        )
# ----------------------------------------------------------------------------------
#  POST PROCESS : SATURATION -VIBRANCE 
# ----------------------------------------------------------------------------------
class Saturation(PostProcess):

    def __init__(self,linearSat=0,gammaSat=0):
        self._linearSaturation = linearSat  # in [-100,100]
        self._gammaSaturation = gammaSat    # in [-100,100]
        self._saturationRange = 1.0

    def setLinearSaturation(self,saturation): self._linearSaturation = saturation

    def setGammaSaturation(self,vibrance): self._gammaSaturation = vibrance

    def postProcess(self, img):
        if self._linearSaturation != 0 or self._gammaSaturation != 0:
            # Convert to hsv once
            imgHSV = skimage.color.rgb2hsv(img)
            satChannel = imgHSV[:, :, 1]

            # Apply linear saturation if enabled
            if self._linearSaturation != 0:
                u = self._linearSaturation / 100
                if u > 0.0:
                    satChannel = (1 - u) * satChannel + u * self._saturationRange
                else:
                    satChannel = (1 + u) * satChannel

            # Apply gamma saturation if enabled
            if self._gammaSaturation != 0:
                if self._gammaSaturation > 0.0:
                    gamma = 1 + (self._gammaSaturation / 25)
                    satChannel = np.power(satChannel, 1 / gamma)
                else:
                    gamma = 1 + (-self._gammaSaturation / 25)
                    satChannel = np.power(satChannel, gamma)

            imgHSV[:, :, 1] = satChannel
            # Convert back to rgb once
            img = skimage.color.hsv2rgb(imgHSV)

        return img

    def toXML(self):
        return (
            f'\t\t<POSTPROCESS name="saturation">\n'
            f'\t\t\t<CHROMA type="saturation">\n'
            f'\t\t\t\t<LINEAR>{self._linearSaturation}</LINEAR>\n'
            f'\t\t\t\t<GAMMA>{self._gammaSaturation}</GAMMA>\n'
            f'\t\t\t</CHROMA>\n'
            f'\t\t</POSTPROCESS>'
        )
# ----------------------------------------------------------------------------------
#  POST PROCESS : AE_YMEAN - Automatic Exposure Ymean-> Ytarget
# ----------------------------------------------------------------------------------
class AE_Ymean(PostProcess):

    def __init__(self,Ytarget=0.5,exposure=0.0):
        self._Ytarget = Ytarget
        self._exposureON = exposure
        self._exposureOFF = exposure
        self._on_off = True

    def setOnOff(self,on_off): self._on_off = on_off

    def setExposure(self,exposureValue):
        if self._on_off: self._exposureON = exposureValue
        else: self._exposureOFF = exposureValue

    def postProcess(self,img):
        if self._on_off: 
            # compute mean Y (Luminance)
            ymeanb = image2Ymean(img)
            if ymeanb == 0.0: ymeanb = 1e-5
            imgOut = img*(self._Ytarget/ymeanb)*math.pow(2,self._exposureON)
        else: 
            imgOut = img*math.pow(2,self._exposureOFF)

        return imgOut

    def toXML(self):
        return (
            f'\t\t<POSTPROCESS name="auto exposure">\n'
            f'\t\t\t<LUMINANCE type="AE">\n'
            f'\t\t\t\t<Y>{self._Ytarget}</Y>\n'
            f'\t\t\t</LUMINANCE>\n'
            f'\t\t</POSTPROCESS>'
        )
# ----------------------------------------------------------------------------------
class PPClip(PostProcess):

	def __init__(self,minValue=0.0,maxValue=1.0):
		self._minValue = minValue
		self._maxValue = maxValue
	
	def postProcess(self,img):
		return np.clip(img,self._minValue,self._maxValue)

