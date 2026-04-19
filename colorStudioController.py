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

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QFileDialog
from PyQt6.QtGui import QIcon, QPixmap, QImage
from PyQt6 import QtCore

import colorStudioModel

# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------

class CSController:
    def __init__(self, root = None, scene=None, widget=None , controlledWidget = None):
        # attributes
        # controlledWidget
        self._controlledWidget = controlledWidget
        # sceneRoot
        self._sceneRoot = root
        # scene compoment controlled
        self._scene = scene
        # widget update after sceneRoot.render()
        self._widget = widget
    # methods
    # event method called by widget
    def _event(self,widget,event):
        pass
# ----------------------------------------------------------------------------------
class CSLightController(CSController):
    def __init__(self,root,light,widget,cwidget=None, cwController = None):
        super().__init__(root,light,widget, controlledWidget =cwidget)
        self._colorWheelController = cwController

    def _event(self,widget,event):
        eventType = event[0]
        # 0  : slider position
        # -1 : decrease Expoosure
        # +1 : increase exposure
        # +2 : change light color

        if eventType == 0 :
            # change light position index
            self._scene.setImageIdx(event[1])  #event[1] slider position 
            # render scene
            img = self._sceneRoot.render()
            # send new image to widget(s)
            for w in self._widget:
                w._update(img)

        if eventType == 2 :
            # tell colorWheel controller that self._scene is active light
            self._colorWheelController._controlledWidget.setWindowTitle("Color Wheel::"+self._scene._name)
            self._colorWheelController._scene =  self._scene

        if eventType == -1 or eventType == 1: 
            # change light exposure
            self._scene.setExposure(event[1]) #event[1] exposure value
            # render scene
            img = self._sceneRoot.render()
            # send new image to widget(s)
            for w in self._widget:
                w._update(img)
# ----------------------------------------------------------------------------------
class CSAEController(CSController):
    def __init__(self,root,postprocess,widget,cwidget=None):
        super().__init__(root,postprocess,widget, controlledWidget =cwidget)

    def _event(self,widget,event):
        eventType = event[0]
        # 0  : on off
        # -1 : decrease Expoosure
        # +1 : increase exposure

        if eventType == 0 :
            # turn on off automatic exposure
            self._scene.setOnOff(event[1])  #event[1] on/off value 
            # render scene
            img = self._sceneRoot.render()
            # send new image to widget(s)
            for w in self._widget:
                w._update(img)

        if eventType == -1 or eventType == 1: 
            # change automtic exposure  value
            self._scene.setExposure(event[1]) #event[1] exposure value
            # render scene
            img = self._sceneRoot.render()
            # send new image to widget(s)
            for w in self._widget:
                w._update(img)
# ----------------------------------------------------------------------------------
class CSColorWheelController(CSController):
    def __init__(self,root,light,widget,cwidget=None):
        super().__init__(root,light,widget,controlledWidget =cwidget)

    def _event(self,widget,event):
        eventType = event[0]
        # 0 : change color

        if eventType == 0 :
            # change light color
            if not self._scene == None:
                self._scene.setColor(event[1])  #event[1] color in RGB
                # render scene
                img = self._sceneRoot.render()
                # send new image to widget(s)
                for w in self._widget:
                    w._update(img)
# ----------------------------------------------------------------------------------
class CSSaturationController(CSController):
    def __init__(self,root,postprocess,widget,cwidget=None):
        super().__init__(root,postprocess,widget, controlledWidget =cwidget)

    def _event(self,widget,event):
        eventType = event[0]
        # 0  : set linear saturation 
        # 1  : set gamma saturation 

        if eventType == 0 :
            # set linear saturation
            self._scene.setLinearSaturation(event[1])  #event[1] saturation value 
        if eventType == 1 :
            # set gamma saturation
            self._scene.setGammaSaturation(event[1])  #event[1] saturation value        # render scene
        img = self._sceneRoot.render()
        # send new image to widget(s)
        for w in self._widget:
            w._update(img)

# ----------------------------------------------------------------------------------
class CSLoadSaveController(CSController):
    def __init__(self, root, widget, ui_builder):
        super().__init__(root, None, None, controlledWidget=widget)
        self._ui_builder = ui_builder

    def _event(self, widget, event):
        eventType = event[0]
        # 0: Load setup XML
        # 1: Save setup XML

        if eventType == 0:
            # Load
            filename, _ = QFileDialog.getOpenFileName(
                None,
                "Select Light Setup XML File",
                "./",
                "XML files (*.xml)"
            )
            if filename:
                print("ColorStudio: Loading XML Setup >", filename)
                self._sceneRoot.clear()
                self._sceneRoot.fromXML(filename, scale=self._ui_builder.template['scale'])
                self._ui_builder.rebuildControls()
                
        elif eventType == 1:
            # Save
            filename, _ = QFileDialog.getSaveFileName(
                None,
                "Save Light Setup XML File",
                "./",
                "XML files (*.xml)"
            )
            if filename:
                if not filename.endswith(".xml"):
                    filename += ".xml"
                print("ColorStudio: Saving XML Setup >", filename)
                xml_data = self._sceneRoot.toXML()
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(xml_data)

# ----------------------------------------------------------------------------------
class CSWhiteBalanceController(CSController):
    def __init__(self, root, postprocess, widget, cwidget=None, cwController=None):
        super().__init__(root, postprocess, widget, controlledWidget=cwidget)
        self._colorWheelController = cwController

    def _event(self, widget, event):
        eventType = event[0]
        # 2: change white balance color (active in color wheel)

        if eventType == 2:
            self._colorWheelController._controlledWidget.setWindowTitle("Color Wheel::White Balance")
            self._colorWheelController._scene = self._scene

# ----------------------------------------------------------------------------------
class CSGammaController(CSController):
    def __init__(self, root, postprocess, widget, cwidget=None):
        super().__init__(root, postprocess, widget, controlledWidget=cwidget)

    def _event(self, widget, event):
        eventType = event[0]
        # 0: set gamma correction

        if eventType == 0:
            self._scene.setGamma(event[1])
            img = self._sceneRoot.render()
            for w in self._widget:
                w._update(img)

# ----------------------------------------------------------------------------------
class CSExportController(CSController):
    def __init__(self, root):
        super().__init__(root, None, None, controlledWidget=None)

    def exportImage(self):
        from PyQt6.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getSaveFileName(
            None,
            "Exporter l'image composée",
            "./",
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )
        if filepath:
            try:
                img = self._sceneRoot.render()
                imgExport = (img * 255).astype('uint8')
                imageio.imwrite(filepath, imgExport)
                print(f"Image exported to: {filepath}")
            except Exception as e:
                print(f"Error exporting image: {e}")