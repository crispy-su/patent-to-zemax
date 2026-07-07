import importlib.util, json, unittest
from pathlib import Path

ROOT=Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location("builder",ROOT/"scripts"/"build_lithography_zmx.py")
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
DATA=json.loads((ROOT/"validation"/"EP0770895A2"/"EP0770895A2-embodiment-1.prescription.json").read_text(encoding="utf-8"))
TABLE3=json.loads((ROOT/"validation"/"US20030048547A1"/"US20030048547A1-table-3.prescription.json").read_text(encoding="utf-8"))
ILINE=json.loads((ROOT/"validation"/"JPH11195607A"/"JPH11195607A-figure-7-8.prescription.json").read_text(encoding="utf-8"))
SHANGHAI=json.loads((ROOT/"validation"/"image-batch-20260707"/"CN111381346B"/"CN111381346B-example-2.prescription.json").read_text(encoding="utf-8"))

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
    def test_iline_prescription_track_and_inserted_stop(self):
        self.assertEqual([],builder.validate(ILINE));self.assertEqual(61,len(ILINE["surfaces"]));self.assertEqual(39,ILINE["stop_surface"])
        self.assertAlmostEqual(1100.00017,ILINE["object_distance_mm"]+sum(s["thickness_mm"] for s in ILINE["surfaces"]),places=8)
        self.assertEqual("AS",ILINE["surfaces"][38]["patent_surface_number"])
        self.assertAlmostEqual(31.17056,ILINE["surfaces"][37]["thickness_mm"]+ILINE["surfaces"][38]["thickness_mm"],places=8)
    def test_patent_c1_maps_to_r4_not_r2(self):
        coeff=builder.effective_even_coefficients(TABLE3["surfaces"][19]["asphere"])
        self.assertEqual(0.0,coeff[0]);self.assertAlmostEqual(4.01395910e-8,coeff[1],places=20)
    def test_r20_aspheres_and_object_image_row_mapping(self):
        self.assertEqual([],builder.validate(SHANGHAI));self.assertEqual(39,len(SHANGHAI["surfaces"]));self.assertEqual(27,SHANGHAI["stop_surface"])
        coeff=builder.effective_even_coefficients(SHANGHAI["surfaces"][1]["asphere"])
        self.assertEqual(10,len(coeff));self.assertEqual(0.0,coeff[0]);self.assertEqual(0.0,coeff[-1])
        self.assertAlmostEqual(1100.0,SHANGHAI["object_distance_mm"]+sum(s["thickness_mm"] for s in SHANGHAI["surfaces"]),places=5)
    def test_zernike_characterization_is_not_double_added(self):
        a=TABLE3["surfaces"][19]["asphere"];self.assertEqual("even_asphere_zernike_characterization",a["kind"])
        self.assertEqual(4.01395910e-8,builder.effective_even_coefficients(a)[1]);self.assertIn("49",a["fringe_terms_mm"])
    def test_layout_export_requires_zosapi_script(self):
        self.assertTrue((ROOT/"scripts"/"export_zosapi_layout.py").is_file())
        self.assertFalse((ROOT/"scripts"/"render_sequential_layout.py").exists())
        source=(ROOT/"scripts"/"export_zosapi_layout.py").read_text(encoding="utf-8")
        self.assertIn("non-finite automatic semi-diameters capped only in this layout",source)
    def test_native_na_and_real_ray_aiming_are_required(self):
        source=(ROOT/"scripts"/"build_lithography_zmx.py").read_text(encoding="utf-8")
        self.assertIn("ZemaxApertureType.ObjectSpaceNA",source)
        self.assertIn('target*abs(float(d["magnification"]))',source)
        self.assertNotIn("for _ in range(60)",source)
        self.assertIn("RayAimingMethod.Real",source)
        self.assertIn("UseRobustRayAiming=True",source)
        self.assertIn("UseAdvancedConvergence=True",source)
        self.assertNotIn("ZemaxApertureType.ImageSpaceFNum",source)
    def test_clear_semi_diameters_remain_automatic_and_all_embodiments_are_required(self):
        builder_source=(ROOT/"scripts"/"build_lithography_zmx.py").read_text(encoding="utf-8")
        self.assertNotIn('.SemiDiameter=float(expected["semi_diameter_mm"])',builder_source)
        self.assertIn("rms_spot_diameter_reference",builder_source)
        self.assertIn("reference only; not an optimization eligibility test",builder_source)
        inventory=(ROOT/"scripts"/"validate_embodiment_inventory.py").read_text(encoding="utf-8")
        self.assertIn('status not in ("modeled","unreconstructable")',inventory)

if __name__=="__main__":unittest.main()
