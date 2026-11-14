# 1분 상식 — 쇼츠 자동 제작

한국어 상식 쇼츠 채널 **1분 상식**(YouTube @ilbun_sangsik · Instagram @ilbun_sangsik)의 영상 제작 파이프라인.

- `engine/` 렌더 엔진 (그림 PIL → ffmpeg), 음성(Supertonic 3 남성 sid=5 + 감정 톤), 음성 인식 검사
- `episodes/` 편별 대본·장면 (`ep18.py`가 최신 형식 예시)
- `assets/` 시그니처 서체, 테마 음악
- `docs/STANDARDS.md` 제작 기준
- `AGENTS.md` 자동 작업이 따라야 하는 순서

```bash
./setup.sh                                        # 패키지 + 모델 (최초 1회)
python3 engine/make.py episodes/ep18.py out/ep18.mp4
```
