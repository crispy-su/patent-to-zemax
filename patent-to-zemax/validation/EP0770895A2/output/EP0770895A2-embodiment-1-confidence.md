# Reconstruction confidence report

- Patent: `EP0770895A2`
- Embodiment: 1
- ZOS-API validation: **PASSED**

## Credibility conclusion

The prescription geometry is high-confidence where copied from rendered patent tables and round-tripped through OpticStudio. Field heights are deterministic derivations. Any stop, material, aperture, or asphere interpretation remains explicitly classified in the evidence. Passing structural validation does not by itself reproduce the patent aberration plots.

## Directly copied from patent

- `surfaces[1..54].radius_mm/thickness_mm/index_after` — confidence 0.99: Visually transcribed and cross-checked against Table 1-1 rendered pages (page 11, Table 1-1, continued on pages 12-13)
- `object_distance_mm, back_focal_distance_mm, magnification, image_space_na` — confidence 0.99: Printed in Specifications of First Embodiment (page 11, Table 1-1 header)
- `wavelength_um` — confidence 0.99: Patent states exposure wavelength 248.4 nm (page 8, Detailed description)
- `field.image_heights_mm` — confidence 0.99: Aberration figures label Y=0, 9.24, 13.2 mm (page 30, Figs. 8-10)

## Deterministically derived

- `field.object_heights_mm` — confidence 0.98: Mask-side object heights derived from patent image heights and 1/4 reduction (page 30, Figs. 8-10 and Table 1-1) Calculation: `[0, 9.24, 13.2] / 0.25 = [0, 36.96, 52.8] mm`
- `total_track_mm` — confidence 0.97: Sum of rounded table spacings is 1000.002 mm versus printed L=1000 mm; accepted as table-rounding closure (page 11, Table 1-1) Calculation: `d0 + sum(d1..d54) = 1000.002 mm; printed L = 1000 mm`

## Inferred or implementation-dependent

- `material.zemax_name` — confidence 0.95: Patent says synthetic quartz SiO2; mapped to Zemax MISC/F_SILICA and index is checked at 0.2484 um (page 10, Table definitions)
- `stop_surface` — confidence 0.65: Patent locates AS between L51 and L52 but gives no axial stop coordinate; reconstruction coincides stop with the object-side surface of L52 (page 9, Description and Fig. 4)
- `surfaces[*].semi_diameter_mm` — confidence 0.60: Patent omits clear apertures; OpticStudio automatic semi-diameters are used after field and NA setup
