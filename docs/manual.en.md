# HEIC Converter User Manual (English)

[한국어](manual.ko.md)

> This manual is updated with every new feature. Current version: 0.2.0 (exe, folder batch)

## 1. What it does
iPhones save photos as HEIC (HEIF) by default. HEIC Converter turns them into JPG or PNG files that open everywhere. Everything runs locally on your PC with no internet access. **Source files are never modified or deleted.**

## 2. Install and run
1. Get `HEICConverter.exe` (see "exe 받기" in the README). No installation needed; put it anywhere, e.g. on the desktop.
2. On first run, **"Windows protected your PC"** may appear because the program is not code-signed. Click **More info → Run anyway**.
3. Two ways to convert:
   - **Drag and drop**: drop a folder or HEIC files onto the `HEICConverter.exe` icon. A console window shows progress; press Enter to close it when done.
   - **Command line**: in PowerShell run e.g. `.\HEICConverter.exe D:\Photos\iPhone`. `--help` lists every option.
4. Default: scans all subfolders and writes **JPG next to each original** (quality 92, GPS location removed).

## 3. Supported formats
| Input | Output |
|---|---|
| `.heic`, `.heif`, `.hif` (any case) | `.jpg`, `.png` |

## 4. Conversion options
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

## 5. Folder batch conversion
- Scans all subfolders (`--no-recursive` to disable). Hidden folders/files and 0-byte files are skipped.
- Live Photo `.MOV`, `.AAE` edit sidecars and files that are already JPG/PNG are not converted; they are only counted as "other files".
- Several photos are converted at once (default: CPU cores − 1, max 8; change with `-j`).
- **Output location**: next to the original by default. With `-o D:\Converted`, the selected folder's name and its subfolder structure are recreated (e.g. `D:\Photos\2024\a.heic` → `D:\Converted\Photos\2024\a.jpg`).
- **Name conflicts** (`--conflict`):
  | Value | Behavior |
  |---|---|
  | `rename` (default) | Writes `IMG_1234_1.jpg` etc. |
  | `skip` | Skips if the output exists — use it to convert only new photos on re-runs. |
  | `overwrite` | Replaces the existing file. |
  Names differing only in case (`IMG.HEIC`, `img.heif`) count as the same name.
- **CSV report** (`--report D:\result.csv`): status (ok/skipped/failed), source, output, failure reason and time per file. Saved so Excel shows Korean correctly.
- **Stopping**: press `Ctrl+C`; files in progress finish, the rest are not converted. No broken files are left.

## 6. Command line options
| Option | Default | Description |
|---|---|---|
| `-f`, `--format` | `jpg` | `jpg` or `png` |
| `-q`, `--quality` | `92` | JPG quality 1–100 |
| `--max-size N` | none | Shrink the long edge to N px |
| `--metadata` | `strip_gps` | `keep` / `strip_gps` / `strip_all` |
| `-o`, `--out` | next to source | Output folder |
| `--conflict` | `rename` | `rename` / `skip` / `overwrite` |
| `--no-recursive` | | Ignore subfolders |
| `-j`, `--workers` | cores − 1 | Parallel conversions |
| `--report file.csv` | | Save a CSV report |
| `--lang` | system language | `ko` / `en` |
| `--no-pause` | | Do not wait for Enter at the end (for scripts) |

Exit codes: 0 = all converted, 1 = some failed or nothing to convert, 2 = no input given.

## 7. Troubleshooting
| Symptom | Fix |
|---|---|
| "cannot read image" | The file is damaged, or is not really a HEIC file despite its extension. |
| Window shows only usage | Double-clicking without input only shows usage; drop a folder onto the icon. |
| Korean paths | Supported, including spaces. |

---
Created by LUDA Research Group · contact@ludaresearch.org
