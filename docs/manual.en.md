# HEIC Converter User Manual (English)

[한국어](manual.ko.md)

> This manual is updated with every new feature. Current version: 0.5.0 (GUI window, exe, installer, right-click menu, folder batch)

## 1. What it does
iPhones save photos as HEIC (HEIF) by default. HEIC Converter turns them into JPG or PNG files that open everywhere. Everything runs locally on your PC with no internet access. **Source files are never modified or deleted.**

## 2. Install and run
1. Download the latest `HEICConverter.exe` from the [Releases](https://github.com/luda-data-ai-lab/heic-converter/releases) page (plus `HEICConverter-cli.exe` if you need the command line). No installation needed; put it anywhere, e.g. on the desktop.
2. On first run, **"Windows protected your PC"** may appear because the program is not code-signed. Click **More info → Run anyway**.
3. Three ways to use it:
   - **Window**: double-click `HEICConverter.exe`. Click **Add folder**/**Add files** or drop folders/photos onto the list, pick options, then click **Convert**.
   - **Drop on the icon**: drop a folder or HEIC files onto the `HEICConverter.exe` icon; the window opens and starts converting with your last saved options.
   - **Command line**: in PowerShell run e.g. `.\HEICConverter-cli.exe D:\Photos\iPhone`. `--help` lists every option (section 6).
4. Default: scans all subfolders and writes **JPG next to each original** (quality 92, GPS location removed).

### The window
| Area | Description |
|---|---|
| Add folder / Add files / Remove selected / Clear list | Manage what to convert. The number of HEIC files found is shown below the list. |
| Include subfolders | Turn off to convert only photos directly inside the selected folders. |
| Options | Format, JPG quality, max size, metadata, same-name handling, save location (sections 4–5). Quality is disabled for PNG. |
| Convert / Cancel | Cancel finishes the photos in progress, then stops. |
| Progress bar | Files done and estimated time left. |
| Result table | Status, source, output and message per file; failures in red. |
| Save CSV report / Open output folder | Enabled when a run finishes. |
| Menus | **File**: Add to Explorer right-click menu, Quit · **Language**: switch Korean/English instantly · **Help**: this manual, About |

Options and language are saved to `%APPDATA%\HEICConverter\settings.json` and restored next time.


### Installing with the setup program (optional)
- Run `HEICConverter-Setup-<version>.exe`. It installs for your account only (`%LOCALAPPDATA%\Programs\HEIC Converter`), no admin rights needed.
- A **HEIC Converter** Start menu entry is created; the desktop icon and the Explorer right-click menu are options during setup.
- Uninstall: Windows Settings → Apps → HEIC Converter → Uninstall. The right-click menu is removed too.

### Explorer right-click menu
- Right-click a folder, empty space inside a folder, or a HEIC photo and choose **Convert to JPG/PNG (HEIC Converter)**; the window opens and converts with your last options.
- On Windows 11 it is under **Show more options** (Shift+F10).
- For photos the entry appears only when one photo is selected; for many photos convert the folder or drop them onto the window.
- With the portable exe (not installed), turn it on/off in the window via **File → Add to Explorer right-click menu**. Turn it on again if you move the exe.

## 3. Supported formats
| Input | Output |
|---|---|
| `.heic`, `.heif`, `.hif` (any case) | `.jpg`, `.png` |

### Notes on iPhone photos
- **Portrait shots**: the iPhone stores landscape pixels plus a rotation tag. The converter rotates the pixels, so every viewer shows them upright. Max size applies to the long edge after rotation.
- **HDR (10-bit) photos**: JPG/PNG are saved at 8 bits. Tonal steps shrink slightly; on normal screens the difference is hard to see.
- **Wide color (Display P3)**: the color profile is embedded unchanged, so colors don't wash out. Apps that ignore profiles may show slightly different colors.
- **HEIC files holding several images**: only the primary image is converted.
- **Live Photos**: only the photo (.HEIC) is converted; the video (.MOV) is skipped.

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
- **Stopping**: click **Cancel** (window) or press `Ctrl+C` (command line); files in progress finish, the rest are not converted. No broken files are left.

- **Speed (reference)**: 1,000 12 MP photos → JPG in about 50 s on an 8-core PC (peak memory about 1 GB). Parallel jobs follow your CPU core count automatically (up to 8).

## 6. Command line options (`HEICConverter-cli.exe`)
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
| CLI shows only usage | `HEICConverter-cli.exe` needs a folder argument; run `HEICConverter.exe` for the window. |
| Korean paths | Supported, including spaces. |
| Colors look duller than the original | The viewer ignores color profiles. Check with the Windows Photos app or a web browser. |
| Antivirus blocks the exe | Unsigned exes can be flagged. Make sure it came from Releases, then add an exception. |

---
Created by LUDA Research Group · contact@ludaresearch.org
