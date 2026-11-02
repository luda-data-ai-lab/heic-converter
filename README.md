# HEIC Converter

아이폰 HEIC/HEIF 사진을 PNG/JPG로 일괄 변환하는 Windows 프로그램입니다. 모든 변환은 PC 안에서만 처리하며, 원본 파일은 수정하지 않습니다.

- 사양: [SPEC.md](SPEC.md) · 작업 계획: [DEVIN.md](DEVIN.md)
- 사용자 매뉴얼: [한국어](docs/manual.ko.md) · [English](docs/manual.en.md)

> 현재 단계: 슬라이스 2 — 폴더 일괄 변환 + `HEICConverter.exe`(끌어다 놓기 / 명령줄). 창(GUI)은 다음 슬라이스에서 추가됩니다.

## exe 받기

- **GitHub Actions**: 저장소 → Actions → *Build Windows exe* → 최신 실행 → 하단 Artifacts의 `HEICConverter-exe` (zip 안에 `HEICConverter.exe`)
- **Release**: `v*` 태그를 올리면 Releases 페이지에 `HEICConverter.exe`가 첨부됩니다.
- **직접 빌드**: 아래 개발 환경 준비 후 `.\scripts\build.ps1` → `dist\HEICConverter.exe`

## exe 사용

- HEIC 사진이 든 **폴더(또는 파일)를 `HEICConverter.exe` 아이콘 위에 끌어다 놓으면** 원본 옆에 JPG가 생깁니다.
- 명령줄 예:

```powershell
.\HEICConverter.exe D:\Photos\iPhone                       # JPG, 원본 옆
.\HEICConverter.exe D:\Photos\iPhone -f png -o D:\Converted   # PNG, 지정 폴더(구조 유지)
.\HEICConverter.exe D:\Photos -q 85 --max-size 2048 --metadata keep --report D:\result.csv
.\HEICConverter.exe --help
```

## 개발 환경 (Windows PowerShell)

```powershell
# uv 설치 (처음 한 번)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"

cd D:\01_luda\project\luda-data-ai-lab\heic-converter
uv sync            # Python 3.12 + 의존성 자동 설치 (.venv)
uv run heic-convert D:\Photos\iPhone   # exe 없이 바로 실행
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
