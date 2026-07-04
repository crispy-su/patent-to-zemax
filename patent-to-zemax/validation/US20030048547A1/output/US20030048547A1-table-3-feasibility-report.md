# US20030048547A1 Table 3 feasibility report

## Conclusion

PASS. The skill reconstructs this dry, all-refractive 193 nm lithography objective as an OpticStudio sequential ZMX. This proves structural prescription, refractive indices, object fields, native NA aperture, Real Ray Aiming, magnification, and total track. Patent-level aberration equivalence remains unverified.

## System

- Direction: mask/object to wafer/image
- Wavelength: 193.304 nm
- 31 lenses, 63 prescription surfaces, 65 Zemax surfaces including object and image
- Wafer field: 10.5 x 26 mm; maximum mask-side object height: 56.08 mm

## ZOS-API results

- Status: `passed`
- Native aperture type: `ObjectSpaceNA`
- Solved OBNA: `0.272726711774549`
- Target image-space NA: `0.75`; measured ISNA: `0.749999999999999`
- Ray aiming: `Real`; persisted after save and reopen
- Maximum-field magnification: `-0.249999809033697`
- Total track: `1000.000999994000` mm
- Surface, material-index, field, wavelength, stop, asphere, and semi-diameter checks: PASS

## Key implementation findings

1. MISC/F_SILICA and MISC/CAF2 do not cover 193.304 nm. Patent single-wavelength indices are used as exact model media.
2. Patent C1 starts at h^4, so the Zemax h^2 coefficient remains zero.
3. ZER9/16/25/36/49 are retained as an alternate characterization, not added a second time to C1-C9.
4. Zemax has no ImageSpaceNA aperture enum for this finite-conjugate workflow. The final file uses ObjectSpaceNA and solves OBNA against ISNA.
5. Real Ray Aiming is enabled before the NA solve and is verified again after reopening the saved ZMX.
6. Layout is exported by reopening the final ZMX through ZOS-API and reading the LDE; no GUI automation is used.

## SHA-256

- Source PDF: `84a358b36da6db46f293dd4c35755fc569b6bfbac0008ecdee88f1e3e01c8881`
- `US20030048547A1-embodiment-table-3.zmx`: `4be6c7f65b12f79193b6df17788a429ea2f02048321b6bfdcff270e58e235d4e`
- `US20030048547A1-embodiment-table-3.prescription.json`: `03f7f782943fe8bda25f5abf7acc1520342fe2779d78744f10e05a31d2c0e5fc`
- `US20030048547A1-embodiment-table-3-zosapi-validation.json`: `55d7c51e78920dc94046e3085060aaec099594d9e9b2359136303f1e4afaa03b`
- `US20030048547A1-table-3-patent-figure-3.png`: `bbb4612306223366445b625c64846d6069dbee05550f1fbb73489f4fbbe44e6a`
- `US20030048547A1-table-3-zosapi-layout.png`: `cf245395d6aa5c153f849479603a03035bdb1fafc735c74c7165ccaf29736b95`
- `US20030048547A1-table-3-comparison.png`: `bd1c393bccaf9f6a862c5782b8444825982c69b6a747b929864061cf464aa524`
