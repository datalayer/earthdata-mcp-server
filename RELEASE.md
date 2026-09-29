<!--
  ~ Copyright (c) 2023-2026 Datalayer, Inc.
  ~
  ~ BSD 3-Clause License
-->

# Making a new release of earthdata_mcp_server

A release is a tag. Pushing `vX.Y.Z` runs the [Release](.github/workflows/release.yaml)
workflow, which:

1. checks the tag names the version in `earthdata_mcp_server/__version__.py`, and fails otherwise;
2. skips the publish when that version is already on PyPI;
3. builds the sdist and the wheel, and publishes them to PyPI with no stored token;
4. creates the GitHub release, with generated notes.

## Cutting one

```bash
# 1. Set the version, and say what changed in CHANGELOG.md.
$EDITOR earthdata_mcp_server/__version__.py CHANGELOG.md
git commit -am "Release 0.5.1" && git push origin main

# 2. Tag it — `make release` refuses a dirty tree — and push the tag.
make release
git push origin v0.5.1
```

Tag from `main`, after the [Build](.github/workflows/build.yaml) workflow is green
on the commit being tagged: it runs the same build and checks the wheel installs
and is discovered by a `reactor_mcp_server` host.

## Trusted publishing setup

PyPI trusts the workflow file rather than a token (OIDC trusted publishing). Once,
on the `earthdata-mcp-server` project on PyPI, add a trusted publisher with:

| Field | Value |
| --- | --- |
| Owner | `datalayer` |
| Repository | `earthdata-mcp-server` |
| Workflow | `release.yaml` |
| Environment | `pypi` |

and create the `pypi` environment in the repository's settings on GitHub.

## By hand

When the workflow cannot run, build from a clean checkout of the tag and upload:

```bash
git clean -fdx
python -m pip install build twine
python -m build
twine upload dist/*
```

## Docker image

```bash
make build-docker push-docker   # tags datalayer/earthdata-mcp-server:<version> and :latest
```
