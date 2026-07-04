#!/usr/bin/env python3
"""Prepare an auditable email package for patent-to-Zemax results.

This script never connects to a mail service and never sends mail.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import zipfile
from email.message import EmailMessage
from email.policy import default
from pathlib import Path


OUTLOOK_DIRECT_ATTACHMENT_LIMIT = 3 * 1024 * 1024
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def describe(path: Path, role: str) -> dict:
    size = path.stat().st_size
    return {
        "role": role,
        "name": path.name,
        "path": str(path.resolve()),
        "bytes": size,
        "sha256": sha256(path),
        "outlook_direct_attachment_eligible": size < OUTLOOK_DIRECT_ATTACHMENT_LIMIT,
    }


def validate_file(path: Path, role: str, suffixes: set[str]) -> Path:
    path = path.resolve()
    if not path.is_file():
        raise ValueError(f"{role} file does not exist: {path}")
    if path.suffix.lower() not in suffixes:
        raise ValueError(f"Unexpected {role} extension {path.suffix}; expected {sorted(suffixes)}")
    return path


def build_package(args: argparse.Namespace) -> dict:
    recipients = list(dict.fromkeys(args.recipient))
    invalid = [address for address in recipients if not EMAIL_RE.match(address)]
    if invalid:
        raise ValueError(f"Invalid recipient address(es): {', '.join(invalid)}")

    patent = validate_file(Path(args.patent), "patent", {".pdf"})
    report = validate_file(Path(args.report), "report", {".md", ".pdf", ".txt"})
    zmx = validate_file(Path(args.zmx), "ZMX", {".zmx"})
    attachments = [describe(patent, "original_patent"), describe(report, "final_report"), describe(zmx, "final_zmx")]

    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    stem = args.package_name or zmx.stem
    subject = args.subject or f"{zmx.stem} 专利复现文件"
    body = args.body or (
        "您好，\n\n附件为光学专利复现资料：原专利、最终报告和 Zemax ZMX 文件。"
        "文件名称、大小和 SHA-256 校验值见随附交付清单。\n\n请查收。"
    )

    manifest = {
        "schema_version": 1,
        "delivery_state": "prepared_not_sent",
        "recipients": recipients,
        "subject": subject,
        "body_format": "text/plain; charset=utf-8",
        "attachments": attachments,
        "outlook_direct_attachment_limit_bytes": OUTLOOK_DIRECT_ATTACHMENT_LIMIT,
        "all_direct_attachments_eligible": all(item["outlook_direct_attachment_eligible"] for item in attachments),
        "send_requires_explicit_confirmation": True,
    }
    manifest_path = output / f"{stem}-email-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    body_path = output / f"{stem}-email-body.txt"
    body_path.write_text(body + "\n", encoding="utf-8")

    zip_path = output / f"{stem}-email-attachments.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in attachments:
            archive.write(item["path"], arcname=item["name"])
        archive.write(manifest_path, arcname=manifest_path.name)

    message = EmailMessage()
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message.set_content(body)
    for item in attachments:
        path = Path(item["path"])
        content_type, _ = mimetypes.guess_type(path.name)
        maintype, subtype = (content_type or "application/octet-stream").split("/", 1)
        message.add_attachment(path.read_bytes(), maintype=maintype, subtype=subtype, filename=path.name)
    message.add_attachment(
        manifest_path.read_bytes(), maintype="application", subtype="json", filename=manifest_path.name
    )
    eml_path = output / f"{stem}-email-draft.eml"
    eml_path.write_bytes(message.as_bytes(policy=default))

    manifest["prepared_files"] = {
        "manifest": str(manifest_path),
        "body": str(body_path),
        "eml_draft": str(eml_path),
        "zip_fallback": str(zip_path),
        "zip_bytes": zip_path.stat().st_size,
        "zip_outlook_direct_attachment_eligible": zip_path.stat().st_size < OUTLOOK_DIRECT_ATTACHMENT_LIMIT,
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--patent", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--zmx", required=True)
    parser.add_argument("--recipient", action="append", required=True, help="Repeat for multiple recipients")
    parser.add_argument("--subject")
    parser.add_argument("--body")
    parser.add_argument("--package-name")
    parser.add_argument("--output-dir", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    try:
        result = build_package(parse_args())
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
