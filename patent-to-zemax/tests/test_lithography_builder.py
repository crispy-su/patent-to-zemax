import importlib.util, json, unittest
from pathlib import Path

ROOT=Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location("builder",ROOT/"scripts"/"build_lithography_zmx.py")
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
DATA=json.loads((ROOT/"validation"/"EP0770895A2"/"EP0770895A2-embodiment-1.prescription.json").read_text(encoding="utf-8"))
TABLE3=json.loads((ROOT/"validation"/"US20030048547A1"/"US20030048547A1-table-3.prescription.json").read_text(encoding="utf-8"))

class TestLithographyBuilder(unittest.TestCase):
    def test_schema_contract(self):self.assertEqual([],builder.validate(DATA))
    def test_first_embodiment_surface_count(self):self.assertEqual(54,len(DATA["surfaces"]))
    def test_track_closure(self):self.assertAlmostEqual(1000.002,DATA["object_distance_mm"]+sum(s["thickness_mm"] for s in DATA["surfaces"]),places=9)
    def test_object_fields_are_derived_from_image_fields(self):
        expected=[x/abs(DATA["magnification"]) for x in DATA["field"]["image_heights_mm"]]
        self.assertEqual(expected,DATA["field"]["object_heights_mm"])
    def test_zmx_contains_image_na_strategy_inputs(self):
        text=builder.initial_zmx(DATA);self.assertEqual(54,text.count("  CURV ")-2);self.assertIn("  STOP",text);self.assertNotIn("OBNA",text)
    def test_table3_schema_and_track(self):
        self.assertEqual([],builder.validate(TABLE3));self.assertEqual(63,len(TABLE3["surfaces"]));self.assertAlmostEqual(1000.000999994,TABLE3["object_distance_mm"]+sum(s["thickness_mm"] for s in TABLE3["surfaces"]),places=9)
    def test_table3_uses_all_four_exact_index_media(self):
        text=builder.initial_zmx(TABLE3);self.assertGreaterEqual(text.count("GLAS ___BLANK"),64)
        self.assertIn("1.56028895",text);self.assertIn("1.50143563",text);self.assertIn("0.999712",text);self.assertIn("0.999982",text)
    def test_patent_c1_maps_to_r4_not_r2(self):
        coeff=builder.effective_even_coefficients(TABLE3["surfaces"][19]["asphere"])
        self.assertEqual(0.0,coeff[0]);self.assertAlmostEqual(4.01395910e-8,coeff[1],places=20)
    def test_zernike_characterization_is_not_double_added(self):
        a=TABLE3["surfaces"][19]["asphere"];self.assertEqual("even_asphere_zernike_characterization",a["kind"])
        self.assertEqual(4.01395910e-8,builder.effective_even_coefficients(a)[1]);self.assertIn("49",a["fringe_terms_mm"])
    def test_layout_export_requires_zosapi_script(self):
        self.assertTrue((ROOT/"scripts"/"export_zosapi_layout.py").is_file())
        self.assertFalse((ROOT/"scripts"/"render_sequential_layout.py").exists())
    def test_native_na_and_real_ray_aiming_are_required(self):
        source=(ROOT/"scripts"/"build_lithography_zmx.py").read_text(encoding="utf-8")
        self.assertIn("ZemaxApertureType.ObjectSpaceNA",source)
        self.assertIn("RayAimingMethod.Real",source)
        self.assertIn("UseRobustRayAiming=True",source)
        self.assertIn("UseAdvancedConvergence=True",source)
        self.assertNotIn("ZemaxApertureType.ImageSpaceFNum",source)

if __name__=="__main__":unittest.main()
