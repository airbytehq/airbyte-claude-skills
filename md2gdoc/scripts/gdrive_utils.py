"""Google Drive utility commands for the md2gdoc skill.

Replaces inline bash $() substitutions in SKILL.md that break in
some shell environments (e.g., zsh with scm_breeze).

Subcommands:
    get-doc-url <gdrive_folder> <basename>
        Find an uploaded file in Google Drive and print its Google Docs URL.

    get-access-token
        Extract a fresh OAuth access token from rclone config.

    set-pageless <file_id>
        Set a Google Doc to pageless mode via the Docs API.

Usage:
    python3 gdrive_utils.py get-doc-url "My Folder" "my-spec"
    python3 gdrive_utils.py get-access-token
    python3 gdrive_utils.py set-pageless "1aBcDeFgHiJkLmNoPqRsTuVwXyZ"
"""

import json
import subprocess
import sys
import urllib.error
import urllib.request


def _get_access_token() -> str:
    """Extract a fresh OAuth access token from rclone config.

    Runs 'rclone about gdrive:' to force token refresh, then
    parses the token from 'rclone config dump'.
    """
    subprocess.run(
        ["rclone", "about", "gdrive:"],
        capture_output=True, text=True, timeout=30,
    )
    result = subprocess.run(
        ["rclone", "config", "dump"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        print(f"Error: rclone config dump failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    config = json.loads(result.stdout)
    token_str = config.get("gdrive", {}).get("token", "")
    if not token_str:
        print("Error: no token found in rclone config for 'gdrive' remote", file=sys.stderr)
        sys.exit(1)

    token_data = json.loads(token_str)
    access_token = token_data.get("access_token", "")
    if not access_token:
        print("Error: access_token field missing from rclone gdrive token", file=sys.stderr)
        sys.exit(1)

    return access_token


def cmd_get_doc_url(gdrive_folder: str, basename: str) -> None:
    """Find the uploaded file and print its Google Docs edit URL."""
    result = subprocess.run(
        [
            "rclone", "lsjson",
            f"gdrive:{gdrive_folder}",
            "--include", f"{basename}*",
            "--no-modtime",
        ],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        print(f"Error: rclone lsjson failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    items = json.loads(result.stdout)

    gdoc = next(
        (i for i in items if i.get("MimeType") == "application/vnd.google-apps.document"),
        None,
    )
    docx = next(
        (i for i in items if "wordprocessingml" in i.get("MimeType", "")),
        None,
    )
    found = gdoc or docx

    if not found:
        print(f"Error: no file matching '{basename}*' found in gdrive:{gdrive_folder}", file=sys.stderr)
        sys.exit(1)

    file_id = found["ID"]
    print(f"https://docs.google.com/document/d/{file_id}/edit")


def cmd_get_access_token() -> None:
    """Print a fresh OAuth access token to stdout."""
    print(_get_access_token())


def cmd_set_pageless(file_id: str) -> None:
    """Set a Google Doc to pageless mode via the Docs batchUpdate API."""
    access_token = _get_access_token()

    url = f"https://docs.googleapis.com/v1/documents/{file_id}:batchUpdate"
    payload = json.dumps({
        "requests": [{
            "updateDocumentStyle": {
                "documentStyle": {
                    "documentFormat": {
                        "documentMode": "PAGELESS"
                    }
                },
                "fields": "documentFormat"
            }
        }]
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp.read()
            print(f"Pageless mode set for document {file_id}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        if e.code == 403:
            print(
                f"Warning: Docs API returned 403. The rclone OAuth project may not have "
                f"the Google Docs API enabled. Use Option B (Chrome MCP) or Option C "
                f"(manual) instead.\nDetails: {error_body}",
                file=sys.stderr,
            )
            sys.exit(2)
        else:
            print(f"Error: Docs API returned HTTP {e.code}: {error_body}", file=sys.stderr)
            sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error connecting to Docs API: {e.reason}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 gdrive_utils.py <subcommand> [args...]", file=sys.stderr)
        print("Subcommands: get-doc-url, get-access-token, set-pageless", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "get-doc-url":
        if len(sys.argv) != 4:
            print("Usage: python3 gdrive_utils.py get-doc-url <gdrive_folder> <basename>", file=sys.stderr)
            sys.exit(1)
        cmd_get_doc_url(sys.argv[2], sys.argv[3])

    elif cmd == "get-access-token":
        cmd_get_access_token()

    elif cmd == "set-pageless":
        if len(sys.argv) != 3:
            print("Usage: python3 gdrive_utils.py set-pageless <file_id>", file=sys.stderr)
            sys.exit(1)
        cmd_set_pageless(sys.argv[2])

    else:
        print(f"Unknown subcommand: {cmd}", file=sys.stderr)
        print("Subcommands: get-doc-url, get-access-token, set-pageless", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
