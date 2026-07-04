# Lithography validation pitfalls

Use these checks before accepting a reconstruction.

## Source acquisition

- A URL ending in `.pdf` may return HTML. Verify the file begins with `%PDF`; if Google Patents returns HTML, read its `citation_pdf_url` and download the immutable patentimages object.
- Use OCR only to locate content. Render the table pages and visually confirm every sign, decimal, infinity entry, material, and continuation row.

## Surface and field interpretation

- Decide whether the final numbered row is the image plane. Do not duplicate it as both a prescription surface and the Zemax image surface.
- Confirm whether a printed diameter is full diameter or half/free diameter. A `1/2 Free Diameter` column maps directly to Zemax semi-diameter.
- Locate the stop using both prose and table topology. A plane gas row between the stated lenses may be the stop surface.
- Validate magnification at a small object height and the maximum requested object height. A paraxial pass alone does not detect field interpretation or distortion mistakes.

## Aperture and ray aiming

- Use Zemax `ObjectSpaceNA` as the native aperture type for finite-conjugate lithography models. Do not leave an equivalent image-space F-number in the delivered file.
- Keep the patent image-side NA as a separate target and solve OBNA numerically against the ZOS-API `ISNA` operand.
- Enable `RayAimingMethod.Real`, `UseRobustRayAiming`, and `UseAdvancedConvergence` before the NA solve and before final field traces. The default non-robust search can return plausible but incorrect chief-ray coordinates at large object heights. `UseEnhancedRayAiming` is not a persistence requirement because OpticStudio may disable it when robust aiming is active.
- Cross-check every ambiguous OCR digit against an independent total-track invariant. In narrow patent tables, `7` can be misread as `1`; do not assign the residual to an unpublished final gap when correcting the ambiguous source digit closes the printed object-to-image length.
- Save and reopen the ZMX, then verify aperture type, solved OBNA, actual ISNA, and Real Ray Aiming independently.

## UV materials

- Check catalog wavelength limits before index matching. A familiar material name is unusable if the requested UV wavelength lies outside its `LD` range.
- At a single patent wavelength, use the printed index as a Zemax model medium when no valid catalog entry exists. Preserve the rejected catalog candidate and reason.
- Test each material with ZOS-API `INDX`. Invalid deep-UV catalog evaluation can terminate the OpticStudio API process instead of returning a clean error.

## Aspheres and Zernike data

- Read the printed sag equation. If `C1` multiplies `h^4`, leave Zemax's second-order term zero and place `C1` in the fourth-order cell.
- Do not automatically add a printed Zernike list to a polynomial asphere. It may be an alternate characterization of the same surface.
- Compare both interpretations against independent invariants such as reduction ratio, field mapping, vertex radius, and described surface location. Record the selected interpretation and rejected alternative.
- Resolve numbering differences explicitly: prose may count the object plane while a prescription table starts at surface 0.

## ZOS-API robustness

- Save only after field, wavelength, aperture, materials, stop, semi-diameters, and aspheres are configured.
- Round-trip radius, thickness, material index, semi-diameter, surface count, stop, total track, field, image-space NA, native aperture type, Real Ray Aiming, and magnification.
- Serialize infinite radii as a string such as `"infinity"`; strict JSON cannot encode IEEE infinity.
- Close each OpticStudio application instance. If repeated standalone launches report an initialization race, allow the previous instance to close before retrying.

## Layout export

- Always run `export_zosapi_layout.py` on the final saved ZMX. The script reloads it with ZOS-API and draws from LDE values.
- Do not depend on GUI screenshots, desktop focus, or an unlocked Windows session.
- Treat layout agreement as a topology check. Patent drawings are often schematic, so pixel similarity is not an optical-performance metric.
