# Email delivery

Use this workflow only after the patent reconstruction and its final validation are complete.

1. Run `scripts/prepare_email_delivery.py` with the original patent PDF, final report, final ZMX, exact recipient, and output directory. The script creates a manifest, plain-text body, MIME `.eml` draft, and ZIP fallback. It never sends mail.
2. Check that the manifest lists exactly three required roles: `original_patent`, `final_report`, and `final_zmx`. Compare their absolute paths and SHA-256 values against the artifacts just returned to the user.
3. Show the user the recipients, subject, attachment names, sizes, and any attachment-limit warning. Never silently omit or replace a file.
4. Default to an Outlook draft. Use the Outlook email connector with the three individual absolute paths only when every file is under its direct-attachment limit (currently strictly less than 3 MB per file).
5. If an individual file is too large, attach the generated ZIP only when it is under the connector limit and tell the user that packaging changed. Otherwise provide the `.eml` draft and ask the user to choose another authorized delivery route. Do not invent a cloud link or store credentials.
6. Sending is a separate external action. Send only after the user confirms the exact recipients, subject, and attachment list at action time. Use a plain-text body and retain the sent copy. For a shared mailbox, require the exact mailbox UPN and an explicit request to send on its behalf.
7. After sending, report the delivery timestamp/message identifier supplied by the mail service and retain the preparation manifest. Do not claim delivery merely because a draft or `.eml` exists.

Example preparation command:

```powershell
python scripts/prepare_email_delivery.py --patent source/patent.pdf --report output/report.md --zmx output/model.zmx --recipient reviewer@example.com --output-dir output/email
```
