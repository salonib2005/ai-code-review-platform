import base64
import os

import httpx


GITHUB_API = "https://api.github.com"


def parse_github_url(repo_url: str):
    """
    Extract owner and repository name from a GitHub URL.
    """

    repo_url = repo_url.rstrip("/")
    parts = repo_url.split("/")

    if len(parts) < 2:
        raise ValueError("Invalid GitHub repository URL")

    owner = parts[-2]
    repo = parts[-1]

    return owner, repo


def get_headers():
    """
    Return GitHub API headers.
    """

    token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def get_repository_files(repo_url: str):
    """
    Get source files and their contents from a GitHub repository.
    """

    owner, repo = parse_github_url(repo_url)

    headers = get_headers()

    # Get repository tree
    api_url = (
        f"{GITHUB_API}/repos/"
        f"{owner}/{repo}/git/trees/main?recursive=1"
    )

    response = httpx.get(
        api_url,
        headers=headers,
        timeout=30.0,
    )

    if response.status_code == 404:

        api_url = (
            f"{GITHUB_API}/repos/"
            f"{owner}/{repo}/git/trees/master?recursive=1"
        )

        response = httpx.get(
            api_url,
            headers=headers,
            timeout=30.0,
        )

    response.raise_for_status()

    data = response.json()

    files = []

    allowed_extensions = (
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".java",
        ".cpp",
        ".c",
        ".go",
        ".rs",
    )

    for item in data.get("tree", []):

        if item.get("type") != "blob":
            continue

        path = item.get("path", "")

        if not path.endswith(allowed_extensions):
            continue

        try:

            content_url = (
                f"{GITHUB_API}/repos/"
                f"{owner}/{repo}/contents/{path}"
            )

            content_response = httpx.get(
                content_url,
                headers=headers,
                timeout=30.0,
            )

            content_response.raise_for_status()

            content_data = content_response.json()

            if "content" not in content_data:
                continue

            content = base64.b64decode(
                content_data["content"]
            ).decode(
                "utf-8",
                errors="replace",
            )

            files.append(
                {
                    "path": path,
                    "content": content,
                }
            )

        except Exception as error:

            print(
                f"Error retrieving {path}: {error}"
            )

    return files