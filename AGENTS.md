# 자동 작업 순서 (매일 1편)

이 저장소는 1분 상식 쇼츠를 만든다. 매일 실행되는 자동 작업은 아래 순서를 따른다. 기준은 `docs/STANDARDS.md`.

1. **준비**: `./setup.sh` (패키지 + 모델). 실패하면 원인을 사용자에게 알리고 멈춘다.
2. **주제**: 웹 검색으로 지금 한국에서 궁금해할 상식 주제 3개 후보 → `docs/EPISODES.md`에 없는 것 중 하나 선택.
3. **사실 확인**: 웹 검색으로 대본의 모든 주장 확인. 출처 URL을 메모.
4. **에피소드 파일**: `episodes/ep18.py`를 본보기로 `episodes/epNN.py` 작성 (NN = 다음 번호).
   - LINES(자막 2줄 + 장면 함수), SPOKEN, EMOTIONS, BREATHS, T(제목), Q(첫 질문), EV(효과음)
   - 장면은 kit의 panel/emo/pill/txt/rr/circ/rings/kpop/badge로 그린다.
5. **정지 화면 확인**: `cd episodes && PYTHONPATH=../engine python3 -c` 로 `EP.frame(t)`를 장면마다 저장해 직접 보고, 겹침·잘림·빈 화면을 고친다.
6. **제작**: `python3 engine/make.py episodes/epNN.py out/epNN.mp4`. ASR_LOW_LINES가 있으면 그 줄을 고쳐 다시.
7. **보관**: 완성 영상을 릴리스 `videos`에 올린다:
   `gh release upload videos out/epNN.mp4 --repo dltkrrla/ilbun-sangsik-factory --clobber`
   공개 링크: `https://github.com/dltkrrla/ilbun-sangsik-factory/releases/download/videos/epNN.mp4`
8. **게시 초안**: `vidiq_video_upload`(url=위 링크) → `vidiq_social_post_draft_create`
   - YouTube `UC7oUcUyROSN66ppccV13ndA`: 제목, 설명, 태그, privacyStatus public, publishAt 당일 18:30 KST
   - Instagram `28745912421778128`: 캡션 + 해시태그
9. **알림**: 영상 파일(SendUserFile), 제목·캡션·사실 출처를 `SendUserMessage`로 보내고 "올려라고 답하시면 게시합니다"라고 묻는다. **승인 없이 게시 금지.**
10. **기록**: `docs/EPISODES.md`에 번호·제목·출처 추가, 에피소드 파일과 함께 커밋·푸시.
