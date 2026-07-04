# Reconstruction confidence report

- Patent: `US20030048547A1`
- Embodiment: table-3
- ZOS-API validation: **PASSED**

## Credibility conclusion

The prescription geometry is high-confidence where copied from rendered patent tables and round-tripped through OpticStudio. Field heights are deterministic derivations. Any stop, material, aperture, or asphere interpretation remains explicitly classified in the evidence. Passing structural validation does not by itself reproduce the patent aberration plots.

## Directly copied from patent

- `surfaces[1..63] radius, thickness, material, semi-diameter` — confidence 0.99: Visually checked against rendered Table 3 and Table 3 continued (page 11, PDF pages 11-12 / printed pages 5-6)
- `surface 20 even-asphere and Fringe Zernike data` — confidence 0.99: Copied from the aspheric constants block immediately below Table 3 (page 12, printed page 6)
- `stop_surface` — confidence 0.99: Prose places diaphragm between L21 and L22; Table 3 has plane gas surface 43 between those lenses (page 11, paragraph 0036 and Table 3)

## Deterministically derived

- `surface 20 numbering interpretation` — confidence 0.98: Table marks row 20 A and L10 image-side surface; prose surface No.21 includes object plane as surface 1 (page 12, Table 3 and paragraph 0033)
- `field.object_heights_mm` — confidence 0.98: Mask heights derived from 10.5 x 26 mm wafer field and 4x reduction (page 11, paragraph 0037) Calculation: `wafer half diagonal sqrt(5.25^2+13^2)=14.020 mm; mask half diagonal=56.08 mm`

## Inferred or implementation-dependent

- `material mappings` — confidence 0.95: All four media use exact patent indices as wavelength-local model media; bundled MISC F_SILICA/CAF2 catalogs are outside their wavelength validity at 193.304 nm. (page 12, Table 3 and L710 note)
- `Zernike characterization interpretation` — confidence 0.97: The ZER values are retained as an alternate characterization of the same asphere. Adding them to C1..C9 changes the paraxial magnification from the specified 1/4 to about 0.260, while C1..C9 alone reproduces 0.25 across the field. (page 12, asphere block)
