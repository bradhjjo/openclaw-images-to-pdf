# ClawHub Preparation Notes

Use this checklist before publishing the skill to a registry such as ClawHub.

## Packaging checklist

1. Run tests.
2. Ensure `SKILL.md` matches the current implementation.
3. Remove transient files such as `.venv` and `.pytest_cache`.
4. Regenerate the `.skill` artifact from the current repository state.
5. Confirm the packaged artifact contains only the intended files.

## Suggested commands

```bash
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
python /path/to/package_skill.py /path/to/images-to-pdf ./dist
```

## Versioning guidance

- Bump release notes when adding user-visible features.
- Keep the GitHub release tag aligned with the packaged artifact version.
- Repackage after any SKILL.md or script change.

## Publish metadata checklist

Make sure these stay accurate:
- repository description
- release title and notes
- README examples
- supported options list
- known limitations

## Future publish path

If the `clawhub` CLI is available, the typical next step would be:
- validate package metadata
- publish the packaged `.skill` artifact or synced skill folder

Keep this file repo-only; it should not be copied into the installed skill directory unless distribution tooling requires it.
