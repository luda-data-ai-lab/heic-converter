"""Tiny KO/EN message table shared by the CLI and (later) the GUI."""

from __future__ import annotations

import locale
import os
import sys

MESSAGES: dict[str, dict[str, str]] = {
    "ko": {
        "usage_hint": "HEIC 사진이 든 폴더나 파일을 이 프로그램 아이콘 위에 끌어다 놓으세요.",
        "scanning": "HEIC 파일 찾는 중…",
        "found": "HEIC {count}개 발견 (그 외 파일 {ignored}개는 건너뜀)",
        "nothing": "변환할 HEIC/HEIF 파일이 없습니다.",
        "converting": "{fmt} 변환 중 (동시 작업 {workers}개)",
        "progress": "[{done}/{total}] {status} {name}",
        "summary": "완료: 성공 {ok} · 건너뜀 {skipped} · 실패 {failed} ({seconds:.1f}초)",
        "cancelled": "취소되었습니다. 남은 {count}개는 변환하지 않았습니다.",
        "report": "결과 CSV: {path}",
        "press_enter": "Enter 키를 누르면 창이 닫힙니다…",
        "status_ok": "성공",
        "status_skipped": "건너뜀",
        "status_failed": "실패",
        "status_cancelled": "취소",
    },
    "en": {
        "usage_hint": "Drag a folder or HEIC files onto this program's icon.",
        "scanning": "Looking for HEIC files…",
        "found": "Found {count} HEIC file(s) ({ignored} other file(s) skipped)",
        "nothing": "No HEIC/HEIF files to convert.",
        "converting": "Converting to {fmt} ({workers} parallel workers)",
        "progress": "[{done}/{total}] {status} {name}",
        "summary": "Done: {ok} converted · {skipped} skipped · {failed} failed ({seconds:.1f}s)",
        "cancelled": "Cancelled. {count} file(s) were not converted.",
        "report": "CSV report: {path}",
        "press_enter": "Press Enter to close…",
        "status_ok": "OK",
        "status_skipped": "SKIP",
        "status_failed": "FAIL",
        "status_cancelled": "CANCEL",
    },
}

LANGUAGES = tuple(MESSAGES)


def detect_language() -> str:
    forced = os.environ.get("HEICCONV_LANG", "").lower()
    if forced in MESSAGES:
        return forced
    if sys.platform == "win32":
        try:
            import ctypes

            lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
            return "ko" if lang_id & 0x3FF == 0x12 else "en"
        except Exception:  # noqa: BLE001 - fall back to locale
            pass
    name = (locale.getlocale()[0] or os.environ.get("LANG", "")).lower()
    return "ko" if name.startswith("ko") else "en"


class Translator:
    def __init__(self, lang: str | None = None) -> None:
        self.lang = lang if lang in MESSAGES else detect_language()

    def __call__(self, key: str, **kwargs: object) -> str:
        text = MESSAGES[self.lang].get(key) or MESSAGES["en"][key]
        return text.format(**kwargs) if kwargs else text
