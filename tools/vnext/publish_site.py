"""Publish web/catalogue to the small `site` branch that Vercel builds.

The main repository tree is over 13 GB, far too large for Vercel to clone on every build. The `site` branch holds
only the catalogue files at its root, so a deploy clones a few hundred kilobytes. Nothing in the working tree, the
current branch or the normal index is touched.
"""
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "web/catalogue"
BRANCH = "site"


def git(*args, env=None, text_input=None):
    result = subprocess.run(["git", *args], cwd=ROOT, env=env, input=text_input, capture_output=True, text=True)
    if result.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-m", "--message", default="Update Wonder Chess catalogue site")
    parser.add_argument("--no-push", action="store_true", help="Create the commit locally without pushing")
    args = parser.parse_args()
    index = ROOT / ".git" / "index.site-publish"
    env = dict(os.environ, GIT_INDEX_FILE=str(index), GIT_WORK_TREE=str(SITE))
    try:
        git("add", "-A", ".", env=env)
        tree = git("write-tree", env=env)
    finally:
        index.unlink(missing_ok=True)
    remote = subprocess.run(["git", "ls-remote", "origin", f"refs/heads/{BRANCH}"], cwd=ROOT, capture_output=True,
                            text=True).stdout.split()
    parent = remote[0] if remote else None
    if parent:
        git("fetch", "--quiet", "origin", BRANCH)
        if git("rev-parse", f"{parent}^{{tree}}") == tree:
            print("Site branch already matches web/catalogue; nothing to publish")
            return
    # Reuse the repository's last author so no git configuration is needed or changed.
    name, email = git("log", "-1", "--format=%an"), git("log", "-1", "--format=%ae")
    identity = dict(os.environ, GIT_AUTHOR_NAME=name, GIT_AUTHOR_EMAIL=email, GIT_COMMITTER_NAME=name,
                    GIT_COMMITTER_EMAIL=email)
    commit = git("commit-tree", tree, *(["-p", parent] if parent else []), env=identity, text_input=args.message + "\n")
    print(f"Site commit {commit[:10]} ({'on ' + parent[:10] if parent else 'first commit'})")
    if not args.no_push:
        # The LFS pre-push hook scans the whole repository; this branch holds no LFS files.
        git("push", "--no-verify", "origin", f"{commit}:refs/heads/{BRANCH}")
        print(f"Pushed to origin/{BRANCH}")


if __name__ == "__main__":
    main()
