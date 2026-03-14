# Publish with GitHub CLI

Run these commands from the repository directory.

## 1) Initialize git

```bash
cd /home/hero/.openclaw/agents/franky/workspace/images-to-pdf-github
git init
git add .
git commit -m "feat: add images-to-pdf OpenClaw skill"
```

## 2) Create the GitHub repository

```bash
gh repo create openclaw-images-to-pdf \
  --public \
  --source=. \
  --remote=origin \
  --push \
  --description "OpenClaw skill for converting multiple image files into a single PDF with deterministic ordering, EXIF correction, alpha flattening, and page layout controls."
```

## 3) Add repository topics

```bash
gh repo edit --add-topic openclaw,skill,pdf,images,image-to-pdf,automation,python,reportlab,pillow,document-processing
```

## 4) Create the first release

```bash
gh release create v0.2.0 \
  --title "v0.2.0 - resilient image-to-pdf workflow improvements" \
  --notes-file RELEASE_NOTES_v0.2.0.md
```

## Optional: attach packaged skill artifact

If you want to ship the packaged `.skill` file too, copy it into this repo or reference its path explicitly:

```bash
gh release create v0.2.0 \
  --title "v0.2.0 - resilient image-to-pdf workflow improvements" \
  --notes-file RELEASE_NOTES_v0.2.0.md \
  /home/hero/.openclaw/agents/franky/workspace/dist/images-to-pdf.skill
```

## Verify auth first

```bash
gh auth status
```
