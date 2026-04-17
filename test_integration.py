# -*- coding: utf-8 -*-
"""
Integration test for ColorStudio to programmatically verify all XML loading,
rendering, and saving features work end-to-end without errors.
Auteurs: KARAMI Anir, ARABAH Yanis
"""

import os
import unittest
import numpy as np
import colorStudioModel

class TestColorStudioIntegration(unittest.TestCase):

    def test_xml_load_render_save_cycle(self):
        """Load, render, save, and reload all existing XML files to verify correctness."""
        xml_files = [
            "xml-postProcess-test.xml"
        ]

        for xml_name in xml_files:
            if not os.path.exists(xml_name):
                print(f"Skipping {xml_name} (file not found)")
                continue

            print(f"\n--- Testing integration cycle for: {xml_name} ---")
            
            # 1. Load scene
            scene_1 = colorStudioModel.Scene()
            # Use small scale (0.1) for super fast test execution
            scene_1.fromXML(xml_name, scale=0.1)
            print("Successfully loaded XML.")

            # 2. Render scene
            img_1 = scene_1.render()
            print(f"Successfully rendered. Shape: {img_1.shape}")
            self.assertIsNotNone(img_1)
            self.assertEqual(len(img_1.shape), 3)

            # 3. Export to temporary XML
            temp_xml_path = f"temp_test_{xml_name}"
            xml_string = scene_1.toXML()
            with open(temp_xml_path, "w", encoding="utf-8") as f:
                f.write(xml_string)
            print("Successfully serialized to XML.")

            # 4. Reload from temporary XML
            scene_2 = colorStudioModel.Scene()
            scene_2.fromXML(temp_xml_path, scale=0.1)
            print("Successfully re-loaded serialized XML.")

            # 5. Render re-loaded scene
            img_2 = scene_2.render()
            print(f"Successfully rendered reloaded scene. Shape: {img_2.shape}")

            # 6. Verify image data equivalence
            np.testing.assert_array_almost_equal(img_1, img_2, decimal=5)
            print("Rendered images are identical!")

            # 7. Check values
            self.assertEqual(len(scene_1._lights), len(scene_2._lights))
            for l1, l2 in zip(scene_1._lights, scene_2._lights):
                self.assertEqual(l1._name, l2._name)
                self.assertEqual(l1._exposure, l2._exposure)
                self.assertEqual(l1._imageIdx, l2._imageIdx)
                np.testing.assert_array_almost_equal(l1._npColorRGB, l2._npColorRGB)

            # Clean up temp file
            if os.path.exists(temp_xml_path):
                os.remove(temp_xml_path)
            print(f"Successfully completed integration test cycle for: {xml_name}")

if __name__ == '__main__':
    unittest.main()
