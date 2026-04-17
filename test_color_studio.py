# -*- coding: utf-8 -*-
"""
Tests unitaires pour le modèle mathématique de ColorStudio.
Auteurs: KARAMI Anir, ARABAH Yanis (BUT3 INFO - APP Parcours A - 2026)
SAE Maintenance Logicielle 2026
"""

import unittest
import numpy as np
import colorStudioModel

class TestColorStudioModel(unittest.TestCase):

    def setUp(self):
        """Initialisation de l'environnement de test."""
        # Création d'une scène de test
        self.scene = colorStudioModel.Scene()
        
        # Création d'une lampe de test
        self.light = colorStudioModel.Light("TestLight")

    def test_light_initialization(self):
        """Test de l'initialisation par défaut d'une lampe."""
        self.assertEqual(self.light._name, "TestLight")
        self.assertEqual(self.light._imageIdx, 0)
        self.assertEqual(self.light._exposure, 0.0)
        np.testing.assert_array_almost_equal(self.light._npColorRGB, np.array([1.0, 1.0, 1.0]))

    def test_light_color_modification(self):
        """Test de la modification de la couleur d'une lampe."""
        new_color = [0.5, 0.2, 0.8]
        self.light.setColor(new_color)
        np.testing.assert_array_almost_equal(self.light._npColorRGB, np.array(new_color))

    def test_light_exposure_modification(self):
        """Test de la modification de l'exposition d'une lampe."""
        self.light.setExposure(1.5)
        self.assertEqual(self.light._exposure, 1.5)
        self.assertTrue(self.light._needUpdate)

    def test_auto_exposure_algorithm(self):
        """Test de l'algorithme d'exposition automatique."""
        ae = colorStudioModel.AE_Ymean(Ytarget=0.5, exposure=1.0)
        self.assertEqual(ae._Ytarget, 0.5)
        self.assertEqual(ae._exposureON, 1.0)
        self.assertTrue(ae._on_off)
        
        # Test de l'activation/désactivation
        ae.setOnOff(0)
        self.assertFalse(ae._on_off)
        ae.setOnOff(1)
        self.assertTrue(ae._on_off)

    def test_saturation_algorithm(self):
        """Test de l'algorithme de saturation."""
        sat = colorStudioModel.Saturation()
        self.assertEqual(sat._linearSaturation, 0.0)
        self.assertEqual(sat._gammaSaturation, 0.0)
        
        sat.setLinearSaturation(10)
        self.assertEqual(sat._linearSaturation, 10)
        
        sat.setGammaSaturation(-5)
        self.assertEqual(sat._gammaSaturation, -5)

    def test_scene_post_processes(self):
        """Test de la gestion des post-processus dans la scène."""
        ae = colorStudioModel.AE_Ymean()
        sat = colorStudioModel.Saturation()
        
        self.scene.addPostProcess(ae)
        self.scene.addPostProcess(sat)
        
        self.assertIn(ae, self.scene._postProcesses)
        self.assertIn(sat, self.scene._postProcesses)

    def test_ppclip_algorithm(self):
        """Test du post-processus de clipping (PPClip)."""
        clip = colorStudioModel.PPClip(minValue=0.1, maxValue=0.9)
        self.assertEqual(clip._minValue, 0.1)
        self.assertEqual(clip._maxValue, 0.9)
        
        test_img = np.array([0.0, 0.5, 1.2])
        output_img = clip.postProcess(test_img)
        np.testing.assert_array_almost_equal(output_img, np.array([0.1, 0.5, 0.9]))

    def test_white_balance_algorithm(self):
        """Test du post-processus de balance des blancs."""
        wb = colorStudioModel.WhiteBalance(color=[1.2, 1.0, 0.8])
        np.testing.assert_array_almost_equal(wb._npColorRGB, np.array([1.2, 1.0, 0.8]))
        
        test_img = np.array([0.5, 0.5, 0.5])
        output_img = wb.postProcess(test_img)
        np.testing.assert_array_almost_equal(output_img, np.array([0.6, 0.5, 0.4]))

    def test_gamma_algorithm(self):
        """Test du post-processus de correction gamma."""
        gamma = colorStudioModel.Gamma(gamma=2.0)
        self.assertEqual(gamma._gamma, 2.0)
        
        test_img = np.array([0.25, 1.0, 0.0])
        output_img = gamma.postProcess(test_img)
        # 1 / 2.0 = 0.5, so np.power(0.25, 0.5) = 0.5
        np.testing.assert_array_almost_equal(output_img, np.array([0.5, 1.0, 0.0]))

    def test_xml_serialization(self):
        """Test de la sérialisation XML du pipeline de post-processus."""
        scene = colorStudioModel.Scene()
        scene._whiteBalance.setColor([0.9, 1.0, 1.1])
        scene._autoExposure._Ytarget = 0.45
        scene._gamma.setGamma(2.2)
        scene._saturation.setLinearSaturation(15.0)
        scene._saturation.setGammaSaturation(-5.0)
        
        xml_output = scene.toXML()
        
        # Verify post-processes are correctly serialized in the generated XML
        self.assertIn('<POSTPROCESS name="white balance">', xml_output)
        self.assertIn('<CHROMA type="AWB">', xml_output)
        self.assertIn('<R>0.9</R>', xml_output)
        
        self.assertIn('<POSTPROCESS name="auto exposure">', xml_output)
        self.assertIn('<LUMINANCE type="AE">', xml_output)
        self.assertIn('<Y>0.45</Y>', xml_output)
        
        self.assertIn('<POSTPROCESS name="gamma">', xml_output)
        self.assertIn('<GAMMA>2.2</GAMMA>', xml_output)
        
        self.assertIn('<POSTPROCESS name="saturation">', xml_output)
        self.assertIn('<LINEAR>15.0</LINEAR>', xml_output)
        self.assertIn('<GAMMA>-5.0</GAMMA>', xml_output)

if __name__ == '__main__':
    unittest.main()
