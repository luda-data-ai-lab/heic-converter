# HEIC Converter User Manual (English)

[한국어](manual.ko.md)

> This manual is updated with every new feature. Current version: 0.1.0 (conversion engine)

## 1. What it does
iPhones save photos as HEIC (HEIF) by default. HEIC Converter turns them into JPG or PNG files that open everywhere. Everything runs locally on your PC with no internet access. **Source files are never modified or deleted.**

## 2. Supported formats
| Input | Output |
|---|---|
| `.heic`, `.heif`, `.hif` (any case) | `.jpg`, `.png` |

## 3. Conversion options
| Option | Default | Description |
|---|---|---|
| Output format | JPG | JPG is small; PNG is lossless but about 5–10× larger. |
| JPG quality | 92 | 1–100. At 95 or higher, no chroma subsampling is applied. |
| Max size | Original | Shrinks the long edge to the given px. Never enlarges. |
| Metadata | Strip GPS | **Keep**: date, camera and location / **Strip GPS**: remove location only / **Strip all**: remove all EXIF |
| Color profile | Keep | Keeps the iPhone's Display P3 colors. |
| File date | Keep | Sets the output's modified date to the source's. |

- Rotation is always applied, so photos look the same as on the iPhone.
- Transparent areas become white in JPG; PNG keeps transparency.
- A failed or cancelled conversion never leaves a broken file behind.

## 4. Troubleshooting
| Symptom | Fix |
|---|---|
| "cannot read image" | The file is damaged, or is not really a HEIC file despite its extension. |

---
Created by LUDA Research Group · contact@ludaresearch.org
