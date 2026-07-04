---
name: patent-to-zemax
description: Convert optical-design patents into audited Zemax OpticStudio sequential models, with dedicated support for rotationally symmetric transmissive lithography objectives. Use for CN, US, JP, EP, or WO/PCT patent numbers, PDFs, scans, prescription tables, or mask-to-wafer systems specifying object height, image-side NA, reduction ratio, UV wavelength, refractive indices, free diameters, or lens-layout figures. Generate prescription JSON, ZMX, ZOS-API validation, layout comparisons, confidence reports, and an optional email delivery package containing the original patent, final report, and ZMX.
---

# Patent to Zemax

Build a traceable optical reconstruction. Treat the patent as evidence, never as permission to hide missing data.

## Required workflow

1. Keep the source PDF and calculate its SHA-256.
2. Render and visually inspect every prescription page and the matching patent layout figure. Do not rely on OCR alone.
3. Create a prescription JSON using `references/lithography-prescription-schema.json`.
4. Classify every value as `copied`, `derived`, or `inferred`. Include page, table/figure, original text, calculation, and confidence.
5. Preserve the patent propagation direction. For lithography default to mask/object -> wafer/image.
6. Represent field as object height when requested. Derive mask height from wafer image height and signed magnification only when both are explicit.
7. Preserve patent image-side NA as the verification target. Set Zemax aperture type to `ObjectSpaceNA`, enable `RayAimingMethod.Real`, robust ray aiming, and advanced convergence, then solve the OBNA value through ZOS-API until the `ISNA` merit operand equals the patent image-side NA. Do not copy the image-side NA number directly into OBNA.
8. Map patent refractive index to a catalog material only after checking both catalog wavelength validity and index at the patent wavelength. If the wavelength is outside the catalog range, use the printed single-wavelength index as a Zemax model medium and record the rejected catalog candidate.
9. Copy printed half free diameters into fixed Zemax semi-diameters. If absent, use OpticStudio automatic semi-diameters and mark them as inferred.
10. Read the patent sag equation before mapping coefficients. If `C1` multiplies `h^4`, map it to Zemax's fourth-order term, leaving the second-order term zero. Treat printed Zernike data as an alternate characterization unless the patent explicitly says it is additive; confirm the interpretation against paraxial magnification.
11. Run `scripts/build_lithography_zmx.py PRESCRIPTION --output DIR`, then require surface, field, wavelength, material-index, total-track, magnification, image-space-NA, `ObjectSpaceNA` aperture type, and Real Ray Aiming checks to pass.
12. Run `scripts/export_zosapi_layout.py ZMX --output LAYOUT.png`. Require it to reload the final ZMX through ZOS-API and render only the LDE values read back from OpticStudio. Do not use GUI automation or require an unlocked desktop.
13. Run `scripts/compare_layouts.py` with the rendered patent figure and the ZOS-API layout.
14. Return the PDF, JSON, ZMX, validation JSON, ZOS-API layout, patent figure, comparison image, and confidence report.
15. When email delivery is requested, run `scripts/prepare_email_delivery.py` only after the artifacts are final. Verify the three required attachments by absolute path and SHA-256: original patent PDF, final report, and final ZMX.
16. Default to preparing an Outlook draft. Show recipients, subject, filenames, sizes, and attachment-limit warnings before any send action. Never store mail passwords or silently omit an oversized attachment.
17. Send only after explicit confirmation of the exact recipients, subject, and attachment list. Record the mail service's delivery result separately from the preparation manifest.

## Accuracy rules

- Never copy the patent image-side NA directly into `OBNA` in a mask-to-wafer model. Use `ObjectSpaceNA` as the native Zemax aperture type and solve its value against `ISNA`.
- Always enable Real Ray Aiming with robust aiming and advanced convergence before solving NA or tracing high-NA lithography fields; fail validation if these settings do not persist after reopening the ZMX.
- Never infer clear apertures from the drawing scale. Drawings are schematic unless dimensions prove otherwise.
- Do not use a family member's prescription without verifying that the embodiment and table are identical.
- Fail if copied surface counts, radius signs, thicknesses, or refractive indices differ after ZOS-API roundtrip.
- Label a model `structurally reconstructed` until NA, field, wavelength, material index, and total track pass.
- Label optical performance as unverified unless patent aberrations or independent ray metrics are also reproduced.
- Never call a JSON-only sketch or a desktop screenshot a ZOS-API layout. The exporter must reload the saved ZMX and read surfaces from the OpticStudio LDE.
- Do not use OpticStudio GUI automation for layout export; ZOS-API is the required path even when the desktop is unlocked.
- Never mark an email package as sent when only a manifest, ZIP, `.eml`, or mailbox draft was created.
- Never attach stale intermediate artifacts. Re-run email preparation after any patent, report, or ZMX change so the recorded hashes match the final files.

## Commands

```powershell
python scripts/build_lithography_zmx.py example.prescription.json --output result
python scripts/export_zosapi_layout.py result/example.zmx --output result/example-zosapi-layout.png
python scripts/compare_layouts.py --patent patent-figure.png --zemax zemax-layout.png --output comparison.png
python scripts/prepare_email_delivery.py --patent source/patent.pdf --report output/report.md --zmx output/model.zmx --recipient reviewer@example.com --output-dir output/email
```

Read `references/lithography-reconstruction.md` for field, NA, stop, material, and confidence conventions. Read `references/lithography-validation-pitfalls.md` before implementing UV material or asphere mappings.
Read `references/email-delivery.md` before drafting or sending reconstruction artifacts by email.
