---
name: patent-to-zemax
description: Convert optical-design patents into audited Zemax OpticStudio sequential models, with dedicated support for rotationally symmetric transmissive lithography objectives. Use for CN, US, JP, EP, or WO/PCT patent numbers, PDFs, scans, prescription tables, or mask-to-wafer systems specifying object height, image-side NA, reduction ratio, UV wavelength, refractive indices, free diameters, or lens-layout figures. Generate prescription JSON, ZMX, ZOS-API validation, layout comparisons, confidence reports, and an optional email delivery package containing the original patent, final report, and ZMX.
---

# Patent to Zemax

Build a traceable optical reconstruction. Treat the patent as evidence, never as permission to hide missing data.

## Required workflow

1. Keep the source PDF and calculate its SHA-256.
2. Render and visually inspect every prescription page and the matching patent layout figure. Inventory every embodiment/table before modeling; do not rely on OCR alone.
3. Create a prescription JSON using `references/lithography-prescription-schema.json`.
4. Classify every value as `copied`, `derived`, or `inferred`. Include page, table/figure, original text, calculation, and confidence.
5. Preserve the patent propagation direction. For lithography default to mask/object -> wafer/image.
6. Represent field as object height when requested. Derive mask height from wafer image height and signed magnification only when both are explicit.
7. For a finite-conjugate reduction objective, derive `object_space_na = image_space_na * abs(signed_magnification)`; equivalently divide image-side NA by the positive reduction ratio (for 4X reduction, `0.8 / 4 = 0.2`). Set this value directly with aperture type `ObjectSpaceNA`. Do not tune OBNA to force the `ISNA` operand to equal the patent value. Record actual ISNA independently. If NA or magnification is absent, infer aperture only from optical invariants, F-number, entrance pupil, marginal-ray data, or explicit geometry and lower confidence.
8. Map patent refractive index to a catalog material only after checking both catalog wavelength validity and index at the patent wavelength. If the wavelength is outside the catalog range, use the printed single-wavelength index as a Zemax model medium and record the rejected catalog candidate.
9. Keep every Zemax Clear Semi-Diameter `Automatic`. Preserve printed clear apertures in JSON as source evidence and use them only for clipping/credibility checks; never make them Fixed in the delivered ZMX.
10. Read the patent sag equation before mapping coefficients. If `C1` multiplies `h^4`, map it to Zemax's fourth-order term, leaving the second-order term zero. Treat printed Zernike data as an alternate characterization unless the patent explicitly says it is additive; confirm the interpretation against paraxial magnification.
11. Create `embodiment-inventory.json`, then generate one JSON and one ZMX for every disclosed numerical embodiment/table. Never select only a preferred or best example. Issue an explicit bilingual per-table failure report when a particular table is incomplete. Run `scripts/validate_embodiment_inventory.py`; do not call the patent complete unless it passes.
12. Run `scripts/build_lithography_zmx.py PRESCRIPTION --output OUT --source-pdf PATENT.pdf`. Require surface, field, wavelength, material-index, total-track, magnification, derived object-space NA, `ObjectSpaceNA`, Automatic Clear Semi-Diameters, and Real Ray Aiming checks. Calculate every field's RMS spot diameter with the ZOS-API Standard Spot Diagram and include it in the bilingual confidence report strictly as a reference. Ensure OUT contains the source patent PDF.
13. Run `scripts/export_zosapi_layout.py ZMX --output LAYOUT.png`. Require it to reload the final ZMX through ZOS-API and render only the LDE values read back from OpticStudio. Do not use GUI automation or require an unlocked desktop.
14. Run `scripts/compare_layouts.py` with the rendered patent figure and the ZOS-API layout.
15. Write every report in Chinese and English, including confidence, failure, validation summary, comparison, and batch-index reports.
16. Return the source PDF inside OUT together with JSON, ZMX, validation JSON, ZOS-API layout, patent figure, comparison image, and bilingual confidence report.
17. For a patent batch, finish every requested reconstruction or issue an evidence-backed `unreconstructable` report before calling the batch complete.
18. When email delivery is requested, run `scripts/prepare_email_delivery.py` only after the artifacts are final. Verify the three required attachments by absolute path and SHA-256: original patent PDF, final report, and final ZMX.
19. Default to preparing an Outlook draft. Show recipients, subject, filenames, sizes, and attachment-limit warnings before any send action. Never store mail passwords or silently omit an oversized attachment.
20. Send only after explicit confirmation of the exact recipients, subject, and attachment list. Record the mail service's delivery result separately from the preparation manifest.

## Accuracy rules

- For finite-conjugate lithography, derive OBNA from image-side NA and signed magnification. Treat actual ISNA as a credibility check, not as a target used to overwrite the derived OBNA.
- Always enable Real Ray Aiming with robust aiming and advanced convergence before setting NA or tracing high-NA lithography fields; fail validation if these settings do not persist after reopening the ZMX.
- Never infer clear apertures from the drawing scale. Drawings are schematic unless dimensions prove otherwise.
- Never deliver Fixed Clear Semi-Diameters; leave them Automatic even when the patent prints clear apertures.
- Do not use a family member's prescription without verifying that the embodiment and table are identical.
- Fail if copied surface counts, radius signs, thicknesses, or refractive indices differ after ZOS-API roundtrip.
- Label a model `structurally reconstructed` until NA, field, wavelength, material index, and total track pass.
- Label optical performance as unverified unless patent aberrations or independent ray metrics are also reproduced.
- Report all-field RMS spot diameters as reference values only; do not use them as an optimization gate or include optimization behavior in this skill.
- Never call a JSON-only sketch or a desktop screenshot a ZOS-API layout. The exporter must reload the saved ZMX and read surfaces from the OpticStudio LDE.
- Do not use OpticStudio GUI automation for layout export; ZOS-API is the required path even when the desktop is unlocked.
- Never mark an email package as sent when only a manifest, ZIP, `.eml`, or mailbox draft was created.
- Never attach stale intermediate artifacts. Re-run email preparation after any patent, report, or ZMX change so the recorded hashes match the final files.

## Commands

```powershell
python scripts/build_lithography_zmx.py example.prescription.json --output result --source-pdf patent.pdf
python scripts/validate_embodiment_inventory.py embodiment-inventory.json --output-root result
python scripts/export_zosapi_layout.py result/example.zmx --output result/example-zosapi-layout.png
python scripts/compare_layouts.py --patent patent-figure.png --zemax zemax-layout.png --output comparison.png
python scripts/prepare_email_delivery.py --patent source/patent.pdf --report output/report.md --zmx output/model.zmx --recipient reviewer@example.com --output-dir output/email
```

Read `references/lithography-reconstruction.md` for field, NA, stop, material, and confidence conventions. Read `references/lithography-validation-pitfalls.md` before implementing UV material or asphere mappings.
Read `references/email-delivery.md` before drafting or sending reconstruction artifacts by email.
