# HEIC Converter

아이폰 HEIC/HEIF 사진을 PNG/JPG로 일괄 변환하는 Windows 프로그램입니다. 모든 변환은 PC 안에서만 처리하며, 원본 파일은 수정하지 않습니다.

- 사양: [SPEC.md](SPEC.md) · 작업 계획: [DEVIN.md](DEVIN.md)
- 사용자 매뉴얼: [한국어](docs/manual.ko.md) · [English](docs/manual.en.md)

> 현재 단계: 슬라이스 1 (변환 엔진). GUI와 `.exe`는 슬라이스 3, 4에서 추가됩니다.

## 개발 환경 (Windows PowerShell)

```powershell
# uv 설치 (처음 한 번)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"

cd D:\01_luda\project\luda-data-ai-lab\heic-converter
uv sync            # Python 3.12 + 의존성 자동 설치 (.venv)
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
