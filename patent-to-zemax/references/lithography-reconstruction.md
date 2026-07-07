# Lithography reconstruction conventions

- Keep mask -> wafer orientation unless explicitly reversed.
- Use Zemax Object Height for mask-side field. For magnification `m`, derive `object_height = image_height / abs(m)`.
- Store patent image-side NA separately. For finite-conjugate projection systems set `OBNA = image-side NA * abs(signed magnification)` (or divide by the positive reduction ratio). Keep `ISNA` as an independent readback; do not tune OBNA to force it.
- Use the patent wavelength in micrometres. Validate catalog wavelength limits before checking its index. If the patent wavelength is outside the catalog range, prefer the printed single-wavelength index as a Zemax model medium and retain the rejected catalog mapping in the evidence.
- Keep Clear Semi-Diameters Automatic. Retain printed half free diameters in the evidence model for clipping checks, but do not write them as Fixed LDE values.
- Parse the printed sag equation. Some lithography patents define `C1 h^4`; Zemax also exposes an `r^2` cell, which must remain zero in that convention.
- A Zernike list printed below an even-asphere prescription may characterize the same surface rather than add a second sag. Preserve both representations and reject an additive interpretation if it contradicts the printed reduction ratio or field mapping.
- A stop described only as "between" two lenses has uncertain axial location. Coinciding it with an adjacent surface is an inference and must be reported.
- If clear apertures are unpublished, let OpticStudio compute automatic semi-diameters after fields and aperture are established. These are implementation values, not patent data.
- Confidence guidance: copied and visually cross-checked `0.99`; deterministic arithmetic `0.95`; catalog mapping `0.90-0.98`; stop placement `0.5-0.7`; schematic-only estimates below `0.5`.
- A successful ZMX load proves syntax and structural roundtrip only. It does not prove patent-level aberration performance.
- Export layouts by reloading the final ZMX with `export_zosapi_layout.py`; never require GUI automation or an unlocked desktop.
