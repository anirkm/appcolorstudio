# -*- coding: utf-8 -*-
"""
Color Studio - Rémi Cozot 2019
Auteurs: KARAMI Anir, ARABAH Yanis (BUT3 INFO - APP Parcours A - 2026)
----------------------------------
new version of 
Color Studio - Rémi Cozot 2019
"""
# ----------------------------------------------------------------------------------
# main changes
# ----------------------------------------------------------------------------------
# GUI lib: pygame to pyqt5
# include 3d color point cloud (modernGL) 
# ----------------------------------------------------------------------------------
# version0.0
# -----------------------------------------------------------------------------------
# Qt window

# import(s)
# ----------------------------------------------------------------------------------

import sys
import imageio
import moderngl

import numpy as np
import skimage

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QMainWindow, QScrollArea, QFrame
from PyQt6.QtGui import QIcon

import colorStudioModel
import colorStudioWidget
import colorStudioController
import colorStudioUtils

# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
class CSUIBuilder:
        # class attributes
        uiLoadIMG  	= None
        uiSaveIMG  	= None
        uiAEonIMG  	= None
        uiAEoffIMG 	= None
        uiDEIMG 	= None
        uiIEIMG 	=  None
        uiCCIMG 	=  None

        template1920x1080 = { 'scale': 0.5 ,                     \
            'uiRenderWidget_pos' : (480,30),                    \
            'uiRenderWidget_size' : (int(1920/2),int(1080/2)),  \
            # color3D widget
            'uiColor3DWidget_pos' : (1440,30),                  \
            'uiColor3DWidget_size' : (480,480),                 \
            # color wheel widget
            'uiColorWheelWidget_pos' : (1440,540),              \
            'uiColorWheelWidget_size' : (480,480),              \
            # menu/control widget
            'uiControlWidget_pos' : (0,30),                     \
            'uiControlWidget_size' : (480,0)}

        template3000x200 = { 'scale': 1,                        \
            'uiRenderWidget_pos' : (int(480*1.25),60),          \
            'uiRenderWidget_size' : (int(1920),int(1080)),      \
            # color3D widget
            'uiColor3DWidget_pos' : (3000-480,60),              \
            'uiColor3DWidget_size' : (480,480),                 \
            # color wheel widget
            'uiColorWheelWidget_pos' : (3000-480,540+60),       \
            'uiColorWheelWidget_size' : (480,480),              \
            # menu/control widget
            'uiControlWidget_pos' : (0,60),                     \
            'uiControlWidget_size' : (480,0)}

        template = template1920x1080

        # class method
        def setTemplate(widthSceen,heightScreen):
            if widthSceen == 3000 : CSUIBuilder.template = CSUIBuilder.template3000x200

        # constructor
        def __init__(self):
            pass

        # class method
        def uiLoadIcon(pathUIimg=None):
            if pathUIimg==None: pathUIimg = './images/others/'
            # window with buttons
            CSUIBuilder.uiLoadIMG  	= QIcon(pathUIimg+'uiLoad.png')
            CSUIBuilder.uiSaveIMG  	= QIcon(pathUIimg+'uiSave.png')
            CSUIBuilder.uiAEonIMG  	= QIcon(pathUIimg+'uiAEon.png')
            CSUIBuilder.uiAEoffIMG 	= QIcon(pathUIimg+'uiAEoff.png')
            CSUIBuilder.uiDEIMG 	=  QIcon(pathUIimg+'uiLight_F_DE.png')
            CSUIBuilder.uiIEIMG 	=  QIcon(pathUIimg+'uiLight_F_IE.png')
            CSUIBuilder.uiCCIMG 	=  QIcon(pathUIimg+'uiLight_F_CC.png')
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
class CSUIAllBuilder(CSUIBuilder):
    def createHeader(self, text):
        lbl = QLabel(text)
        lbl.setProperty("header", "true")
        return lbl

    def __init__(self,lightsScene):
        # (0) load qIcon images and get screen resolution
        CSUIBuilder.uiLoadIcon()

        # (1) Create Master MainWindow
        self._mainWindow = QMainWindow()
        self._mainWindow.setWindowTitle("ColorStudio")
        self._mainWindow.resize(1750, 950)

        # Central widget and horizontal layout
        centralWidget = QWidget()
        mainLayout = QHBoxLayout(centralWidget)
        mainLayout.setContentsMargins(15, 15, 15, 15)
        mainLayout.setSpacing(15)

        # (2) Left Panel: Controls Frame with ScrollArea
        leftFrame = QFrame()
        leftFrame.setObjectName("leftFrame")
        leftLayout = QVBoxLayout(leftFrame)
        leftLayout.setContentsMargins(12, 12, 12, 12)
        leftLayout.setSpacing(10)
        leftLayout.addWidget(self.createHeader("CONFIGURATION & PARAMETRES"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self._controlWidget = colorStudioWidget.CSDisplayControls()
        scroll.setWidget(self._controlWidget)
        leftLayout.addWidget(scroll)
        mainLayout.addWidget(leftFrame, stretch=1)

        # (3) Middle Panel: Main Image Render Frame
        middleFrame = QFrame()
        middleFrame.setObjectName("middleFrame")
        middleLayout = QVBoxLayout(middleFrame)
        middleLayout.setContentsMargins(12, 12, 12, 12)
        middleLayout.addWidget(self.createHeader("RENDU COMPOSITE FINAL"))

        self._renderWidget = colorStudioWidget.CSDisplayWidget(None, "Color Studio - RC 2019")
        middleLayout.addWidget(self._renderWidget)
        mainLayout.addWidget(middleFrame, stretch=2)

        # (4) Right Panel: 3D Color Space Frame & Color Wheel Frame
        rightFrame = QFrame()
        rightFrame.setObjectName("rightFrame")
        rightLayout = QVBoxLayout(rightFrame)
        rightLayout.setContentsMargins(12, 12, 12, 12)
        rightLayout.setSpacing(15)

        rightLayout.addWidget(self.createHeader("ESPACE COULEUR 3D (CIE rg)"))
        self._color3DWidget = colorStudioWidget.MyWidgetGL(skimage.transform.rescale(lightsScene.render(), 0.1, anti_aliasing=True, channel_axis =2 ),True)
        self._color3DWidget.setMinimumSize(400, 360)
        rightLayout.addWidget(self._color3DWidget)

        rightLayout.addWidget(self.createHeader("BALANCE & CALIBRATION DES COULEURS"))
        self._colorWheelWidget = colorStudioWidget.CSDisplayColorWheel(None, 400)
        self._colorWheelWidget.setMinimumSize(400, 400)
        rightLayout.addWidget(self._colorWheelWidget)
        mainLayout.addWidget(rightFrame, stretch=1)

        # Connect ColorWheel Controller
        colorWheelController = colorStudioController.CSColorWheelController(lightsScene,None,[self._renderWidget,self._color3DWidget],self._colorWheelWidget)
        self._colorWheelWidget._controller = colorWheelController

        # Store references for rebuilding
        self._lightsScene = lightsScene
        self._colorWheelController = colorWheelController

        # Build initial control layouts
        self.rebuildControls()

        # Premium Dark Mode QSS Stylesheet
        stylesheet = """
        QMainWindow {
            background-color: #121212;
        }
        QWidget {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #b3b3b3;
            font-size: 11px;
        }
        QFrame#leftFrame, QFrame#middleFrame, QFrame#rightFrame {
            background-color: #1a1a1a;
            border-radius: 4px;
            border: 1px solid #2c2c2c;
        }
        QLabel {
            color: #b3b3b3;
        }
        QLabel[header="true"] {
            font-size: 11px;
            font-weight: bold;
            color: #ffffff;
            border-bottom: 1px solid #2c2c2c;
            padding-bottom: 6px;
            margin-bottom: 6px;
        }
        QSlider::groove:horizontal {
            border: 1px solid #2c2c2c;
            height: 4px;
            background: #121212;
            border-radius: 2px;
        }
        QSlider::sub-page:horizontal {
            background: #555555;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #ffffff;
            border: 1px solid #555555;
            width: 10px;
            height: 10px;
            margin: -3px 0;
            border-radius: 5px;
        }
        QSlider::handle:horizontal:hover {
            background: #cccccc;
        }
        QScrollArea {
            background-color: transparent;
            border: none;
        }
        QScrollBar:vertical {
            border: none;
            background: #121212;
            width: 6px;
            border-radius: 3px;
        }
        QScrollBar::handle:vertical {
            background: #2c2c2c;
            border-radius: 3px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background: #444444;
        }
        QPushButton {
            background-color: #222222;
            border: 1px solid #2c2c2c;
            border-radius: 3px;
            padding: 4px 8px;
            font-weight: normal;
            color: #b3b3b3;
        }
        QPushButton:hover {
            background-color: #2a2a2a;
            border: 1px solid #444444;
            color: #ffffff;
        }
        CSQIMGButton {
            background-color: #222222;
            border: 1px solid #2c2c2c;
            border-radius: 3px;
            padding: 2px;
        }
        CSQIMGButton:hover {
            background-color: #2a2a2a;
            border: 1px solid #444444;
        }
        """
        self._mainWindow.setCentralWidget(centralWidget)
        self._mainWindow.setStyleSheet(stylesheet)
        
        # Show master window!
        self._mainWindow.show()

        # (end) init render
        self._renderWidget._update(lightsScene.render())

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def rebuildControls(self):
        # 1. Clear existing control widgets from layout
        self.clearLayout(self._controlWidget._layout)

        # 2. Add Load / Save / Export Setup
        self._controlWidget._layout.addWidget(self.createHeader("SAUVEGARDE & CHARGEMENT"))
        loadSaveLayout = colorStudioWidget.CSQLoadSaveLayout(CSUIBuilder.uiLoadIMG, CSUIBuilder.uiSaveIMG)
        self._controlWidget._layout.addLayout(loadSaveLayout)

        loadSaveController = colorStudioController.CSLoadSaveController(self._lightsScene, loadSaveLayout, self)
        loadSaveLayout._controller = loadSaveController

        exportController = colorStudioController.CSExportController(self._lightsScene)
        loadSaveLayout._export_controller = exportController

        # 3. Light Control Layout per light
        for light in self._lightsScene._lights:
            self._controlWidget._layout.addWidget(self.createHeader(f"{light._name.upper()} (EV / COULEUR / POSITION)"))
            lightControl_layout = colorStudioWidget.CSQLightControlLayout(None, lightPosIdx=light._imageIdx)
            lightControl_layout._exposure = light._exposure
            expoString = "{:+.2f}".format(light._exposure)
            lightControl_layout._exposureValueLabel.setText(expoString)
            self._controlWidget._layout.addLayout(lightControl_layout)
            
            # lightController
            lightController = colorStudioController.CSLightController(self._lightsScene, light, [self._renderWidget, self._color3DWidget])
            lightController._colorWheelController = self._colorWheelController
            lightControl_layout._controller = lightController

        # 4. White Balance (AWB)
        self._controlWidget._layout.addWidget(self.createHeader("BALANCE DES BLANCS"))
        wb_layout = colorStudioWidget.CSQWhiteBalanceLayout(None)
        self._controlWidget._layout.addLayout(wb_layout)
        
        wb_controller = colorStudioController.CSWhiteBalanceController(self._lightsScene, self._lightsScene._whiteBalance, [self._renderWidget, self._color3DWidget], cwController=self._colorWheelController)
        wb_layout._controller = wb_controller

        # 5. Automatic Exposure
        self._controlWidget._layout.addWidget(self.createHeader("EXPOSITION AUTOMATIQUE (AE)"))
        AE_layout = colorStudioWidget.CSQAEControlLayout(None)
        self._controlWidget._layout.addLayout(AE_layout)
        
        ae_controller = colorStudioController.CSAEController(self._lightsScene, self._lightsScene._autoExposure, [self._renderWidget, self._color3DWidget])
        AE_layout._controller = ae_controller

        # 6. Saturation
        self._controlWidget._layout.addWidget(self.createHeader("SATURATION & VIBRANCE"))
        sat_layout = colorStudioWidget.CSQSaturationLayout(None)
        self._controlWidget._layout.addLayout(sat_layout)
        
        sat_controller = colorStudioController.CSSaturationController(self._lightsScene, self._lightsScene._saturation, [self._renderWidget, self._color3DWidget])
        sat_layout._controller = sat_controller

        # 7. Gamma Correction
        self._controlWidget._layout.addWidget(self.createHeader("CORRECTION GAMMA"))
        g_val = self._lightsScene._gamma._gamma
        gamma_layout = colorStudioWidget.CSQGammaLayout(None, defaultGamma=g_val)
        self._controlWidget._layout.addLayout(gamma_layout)
        
        gamma_controller = colorStudioController.CSGammaController(self._lightsScene, self._lightsScene._gamma, [self._renderWidget, self._color3DWidget])
        gamma_layout._controller = gamma_controller

        # Force full update of display widgets
        img = self._lightsScene.render()
        self._renderWidget._update(img)
        self._color3DWidget._update(img)





# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
