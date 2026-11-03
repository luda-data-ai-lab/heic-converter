"""Tiny KO/EN message table shared by the CLI and the GUI."""

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
        "app_title": "HEIC Converter — 아이폰 사진 변환",
        "menu_file": "파일",
        "menu_quit": "끝내기",
        "menu_help": "도움말",
        "menu_manual": "사용자 매뉴얼",
        "menu_about": "프로그램 정보",
        "menu_license": "라이선스",
        "menu_shell": "탐색기 우클릭 메뉴에 추가",
        "shell_verb": "JPG/PNG로 변환 (HEIC Converter)",
        "shell_added": "탐색기 우클릭 메뉴에 추가했습니다. 폴더나 HEIC 사진을 마우스 오른쪽 버튼으로 누르세요. (Windows 11: '더 많은 옵션 표시' 안)",
        "shell_removed": "탐색기 우클릭 메뉴에서 제거했습니다.",
        "menu_language": "언어",
        "add_folder": "폴더 추가",
        "add_files": "파일 추가",
        "clear_list": "목록 비우기",
        "remove_selected": "선택 삭제",
        "recursive": "하위 폴더 포함",
        "drop_hint": "HEIC 사진이 든 폴더나 파일을 여기에 끌어다 놓으세요",
        "inputs_count": "대상 {count}개 · HEIC {heic}개",
        "group_options": "변환 옵션",
        "format": "형식",
        "quality": "JPG 품질",
        "max_size": "최대 크기",
        "max_size_original": "원본 유지",
        "metadata": "메타데이터",
        "metadata_keep": "모두 유지",
        "metadata_strip_gps": "GPS 위치만 삭제",
        "metadata_strip_all": "모두 삭제",
        "conflict": "같은 이름",
        "conflict_rename": "번호 붙이기",
        "conflict_skip": "건너뛰기",
        "conflict_overwrite": "덮어쓰기",
        "output": "저장 위치",
        "output_beside": "원본 옆",
        "output_folder": "지정 폴더",
        "browse": "찾아보기…",
        "start": "변환 시작",
        "cancel": "취소",
        "ready": "준비됨",
        "eta": "{done} / {total} · 남은 시간 약 {eta}",
        "result_summary": "성공 {ok} · 건너뜀 {skipped} · 실패 {failed}",
        "save_csv": "결과 CSV 저장",
        "open_output": "출력 폴더 열기",
        "col_status": "상태",
        "col_source": "원본",
        "col_output": "결과",
        "col_message": "메시지",
        "need_inputs": "변환할 폴더나 파일을 먼저 추가하세요.",
        "need_out_dir": "저장할 폴더를 선택하세요.",
        "about_text": "HEIC Converter {version}\n아이폰 HEIC/HEIF 사진을 JPG/PNG로 변환합니다.\n모든 처리는 PC 안에서만 이루어집니다.\n\nCreated by Devin Ambassador James Yeon\njames.jewoo.yeon@gmail.com\n\n비상업적 용도로만 무료로 사용할 수 있습니다 (PolyForm Noncommercial 1.0.0). 판매·재판매·상업적 이용은 허용되지 않습니다. 자세한 내용: 도움말 → 라이선스",
        "footer": "Created by Devin Ambassador James Yeon",
        "csv_filter": "CSV 파일 (*.csv)",
        "heic_filter": "HEIC 사진 (*.heic *.heif *.hif)",
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
        "app_title": "HEIC Converter — iPhone photo converter",
        "menu_file": "File",
        "menu_quit": "Quit",
        "menu_help": "Help",
        "menu_manual": "User manual",
        "menu_about": "About",
        "menu_license": "License",
        "menu_shell": "Add to Explorer right-click menu",
        "shell_verb": "Convert to JPG/PNG (HEIC Converter)",
        "shell_added": "Added to the Explorer right-click menu. Right-click a folder or HEIC photo. (Windows 11: under 'Show more options')",
        "shell_removed": "Removed from the Explorer right-click menu.",
        "menu_language": "Language",
        "add_folder": "Add folder",
        "add_files": "Add files",
        "clear_list": "Clear list",
        "remove_selected": "Remove selected",
        "recursive": "Include subfolders",
        "drop_hint": "Drop folders or HEIC photos here",
        "inputs_count": "{count} item(s) · {heic} HEIC file(s)",
        "group_options": "Options",
        "format": "Format",
        "quality": "JPG quality",
        "max_size": "Max size",
        "max_size_original": "Original",
        "metadata": "Metadata",
        "metadata_keep": "Keep all",
        "metadata_strip_gps": "Strip GPS only",
        "metadata_strip_all": "Strip all",
        "conflict": "Same name",
        "conflict_rename": "Add number",
        "conflict_skip": "Skip",
        "conflict_overwrite": "Overwrite",
        "output": "Save to",
        "output_beside": "Next to original",
        "output_folder": "Folder",
        "browse": "Browse…",
        "start": "Convert",
        "cancel": "Cancel",
        "ready": "Ready",
        "eta": "{done} / {total} · about {eta} left",
        "result_summary": "{ok} converted · {skipped} skipped · {failed} failed",
        "save_csv": "Save CSV report",
        "open_output": "Open output folder",
        "col_status": "Status",
        "col_source": "Source",
        "col_output": "Output",
        "col_message": "Message",
        "need_inputs": "Add a folder or files to convert first.",
        "need_out_dir": "Choose an output folder.",
        "about_text": "HEIC Converter {version}\nConverts iPhone HEIC/HEIF photos to JPG/PNG.\nEverything runs locally on this PC.\n\nCreated by Devin Ambassador James Yeon\njames.jewoo.yeon@gmail.com\n\nFree for noncommercial use only (PolyForm Noncommercial 1.0.0). Selling, reselling or commercial use is not permitted. Details: Help → License",
        "footer": "Created by Devin Ambassador James Yeon",
        "csv_filter": "CSV files (*.csv)",
        "heic_filter": "HEIC photos (*.heic *.heif *.hif)",
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
