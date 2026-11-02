# HEIC Converter

아이폰 HEIC/HEIF 사진을 PNG/JPG로 일괄 변환하는 Windows 프로그램입니다. 모든 변환은 PC 안에서만 처리하며, 원본 파일은 수정하지 않습니다.

- 사양: [SPEC.md](SPEC.md) · 작업 계획: [DEVIN.md](DEVIN.md)
- 사용자 매뉴얼: [한국어](docs/manual.ko.md) · [English](docs/manual.en.md)

> 현재 단계: 슬라이스 3 — 창(GUI) `HEICConverter.exe` + 명령줄 `HEICConverter-cli.exe`.

## exe 받기

- **GitHub Actions**: 저장소 → Actions → *Build Windows exe* → 최신 실행 → 하단 Artifacts의 `HEICConverter-exe` (zip 안에 `HEICConverter.exe`, `HEICConverter-cli.exe`)
- **Release (권장)**: [Releases](https://github.com/luda-data-ai-lab/heic-converter/releases) 페이지에서 받습니다.
  - `HEICConverter-Setup-<버전>.exe`: 설치본 (관리자 권한 불필요, 시작 메뉴 + 탐색기 우클릭 메뉴)
  - `HEICConverter.exe`: 설치 없이 바로 실행 (포터블)
- **소스에서 바로 실행**: `.\scripts\dev.ps1` (창), `.\scripts\dev.ps1 -Cli D:\Photos`, `.\scripts\dev.ps1 -Test`
- **직접 빌드**: 아래 개발 환경 준비 후 `.\scripts\build.ps1` → `dist\HEICConverter.exe`, `dist\HEICConverter-cli.exe` (`-Installer`를 붙이면 설치본도 생성, [Inno Setup 6](https://jrsoftware.org/isinfo.php) 필요)

## exe 사용

- `HEICConverter.exe` **더블클릭** → 창에서 폴더 추가(또는 창에 끌어다 놓기) → 옵션 → **변환 시작**.
- 폴더를 `HEICConverter.exe` **아이콘 위에 끌어다 놓으면** 창이 열리며 저장된 옵션으로 바로 변환합니다.
- 명령줄(`HEICConverter-cli.exe`) 예:

```powershell
.\HEICConverter-cli.exe D:\Photos\iPhone                       # JPG, 원본 옆
.\HEICConverter-cli.exe D:\Photos\iPhone -f png -o D:\Converted   # PNG, 지정 폴더(구조 유지)
.\HEICConverter-cli.exe D:\Photos -q 85 --max-size 2048 --metadata keep --report D:\result.csv
.\HEICConverter-cli.exe --help
```

## 개발 환경 (Windows PowerShell)

```powershell
# uv 설치 (처음 한 번)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"

cd D:\01_luda\project\luda-data-ai-lab\heic-converter
uv sync            # Python 3.12 + 의존성 자동 설치 (.venv)
uv run heic-converter                  # 창(GUI) 실행
uv run heic-convert D:\Photos\iPhone   # 명령줄 실행
uv run pytest -q   # 테스트
uv run ruff check .
```

## 엔진 사용 예 (Python)

```python
from heic_converter.core import convert, ConvertOptions, OutputFormat, MetadataMode

convert("IMG_1234.HEIC", "IMG_1234.jpg")  # JPG q92, GPS 삭제 (기본값)
convert("IMG_1234.HEIC", "IMG_1234.png",
        ConvertOptions(format=OutputFormat.PNG, metadata=MetadataMode.KEEP))
```

---
Created by LUDA Research Group · contact@ludaresearch.org · MIT License

## 릴리스 (관리자)

1. `src/heic_converter/__init__.py`의 `__version__`과 `pyproject.toml`의 `version`을 올리고 PR로 main에 머지합니다.
2. 태그를 올립니다.
   ```powershell
   git checkout main; git pull
   git tag v0.4.0; git push origin v0.4.0
   ```
3. *Build Windows exe* 워크플로가 exe 2개와 설치본을 빌드·점검한 뒤 Releases에 자동으로 첨부합니다.
