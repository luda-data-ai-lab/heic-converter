# DEVIN.md — 작업 계획 (슬라이스 = PR)

각 슬라이스는 main 기준 PR 1개. 각 PR은 테스트 + 매뉴얼(`docs/manual.ko.md`, `docs/manual.en.md`) 갱신을 포함합니다.

## 공통 규칙
- 구조: `src/heic_converter/{core,batch,gui,i18n}/`, `tests/`, `docs/`, `scripts/`
- 검사: `uv run ruff check .`, `uv run pytest`
- 테스트용 HEIC는 테스트 중 pillow-heif로 생성 (저장소에 큰 바이너리 금지, 실제 아이폰 샘플 1~2장만 `tests/fixtures/`)
- 원본 파일은 어떤 경우에도 수정하지 않음 — 테스트로 보장

## 슬라이스
1. **프로젝트 골격 + 변환 엔진** — `pyproject.toml`(uv), ruff/pytest, GitHub Actions(Linux 테스트). `core.convert(src, dst, options)`: HEIC/HEIF → JPG/PNG, Orientation 적용, ICC 유지, EXIF 유지/GPS 삭제/전체 삭제, 품질·리사이즈, 알파 합성, 임시파일→rename, 수정일 유지. 단위 테스트. 매뉴얼 뼈대.
2. **배치 처리 + CLI + exe (사용자 요청으로 패키징 앞당김)** — 폴더 스캔(하위 폴더, 확장자, 숨김/0바이트/MOV/AAE 건너뜀), 출력 경로 계산(원본 옆 / 지정 폴더 + 구조 유지), 이름 충돌 정책, 병렬 처리, 취소, 진행 콜백, 결과 CSV. `heic-convert` CLI, PyInstaller 단일 `HEICConverter.exe`(폴더를 아이콘에 끌어다 놓기), `windows-latest` 빌드·스모크·Artifact/Release 워크플로, `scripts\build.ps1`.
3. **GUI (PySide6) + exe 2종** — 창 `HEICConverter.exe`(콘솔 없음, 아이콘에 끌어다 놓으면 바로 변환) + 명령줄 `HEICConverter-cli.exe`. 단일 창(SPEC 3.4), 드래그앤드롭, 옵션, 진행률/남은 시간, 결과 목록·CSV·폴더 열기, 설정 저장, 한/영 전환, 도움말 메뉴 → 매뉴얼 열기. pytest-qt 스모크 테스트 + 스크린샷.
4. **exe 마무리** — exe 크기 점검, `scripts\dev.ps1`, 첫 Release(`v0.x`) 안내, 실제 아이폰 사진(P3/HDR/세로) 점검.
5. **마무리** — Inno Setup 설치본(시작 메뉴 바로가기), 탐색기 우클릭 "PNG/JPG로 변환" 메뉴(HKCU, 관리자 권한 불필요), 대용량(1,000장+) 성능 점검, 매뉴얼 PDF.

## 결정 사항 (제안)
1. 저장소 이름: `luda-data-ai-lab/heic-converter`
2. 프로그램 이름(창 제목/exe): **HEIC Converter** (`HEICConverter.exe`)
3. UI 언어: 한국어 + 영어, 시스템 언어 자동
4. 기본 출력 형식: **JPG**, 품질 92
5. 메타데이터 기본값: **GPS만 삭제** (촬영일 등은 유지)
6. 기본 저장 위치: **원본 옆**, 같은 이름은 **번호 붙이기**
7. 배포: GitHub Actions가 만든 `.exe`를 Release에서 다운로드 (코드 서명 없음)
8. 슬라이스 5(설치본·우클릭 메뉴) 진행 여부: 진행 (제안)
9. 브랜딩: 하단에 LUDA Research Group 표기 여부 — 표기 (제안)
