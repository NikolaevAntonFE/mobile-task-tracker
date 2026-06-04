# Mobile Task Tracker Handoff

Last stable version: v50
Last commit: 4c71ccd Show editable no due pill
Repository: https://github.com/NikolaevAntonFE/mobile-task-tracker

## Runtime

- Project path: `C:\Users\User\Documents\Codex\2026-06-02\new-chat\outputs\mobile-task-tracker`
- Server: `python server.py`
- Local URL: `http://127.0.0.1:8787/?v=50`
- Android API base in app: `http://192.168.100.25:8787`
- Telegram mode must stay send-only. Do not add polling/getUpdates/webhooks/reactions.
- Secrets are in local `.env`; do not print or commit it.

## Current State

- Android Capacitor app works.
- Local Android notifications work.
- Telegram reminder sending works.
- GitHub remote is configured and pushed.
- APK v50 was built and sent through Telegram.
- Current UI tabs: `Сегодня`, `Бессрочные`, `Будущие`, `Закрытые`.
- Task cards support inline editing:
  - priority pill opens priority choice;
  - type pill opens type choice;
  - date or `без срока` pill opens date/time editor;
  - card tap opens full edit;
  - `...` opens full edit.
- Choice sheets close by tapping outside the sheet.
- Search auto-collapses when empty and blurred.
- `Сегодня` groups tasks by `Просрочено`, `Утро`, `День`, `Вечер`, `Без времени`.

## Main Files

- `index.html`: UI, styles, client state, parser, notifications, API calls.
- `server.py`: HTTP API, task storage, Telegram send-only reminders.
- `sw.js`: service worker cache version.
- `www/`: bundled web assets for Android.
- `android/`: Capacitor Android project.

## Next Product Step

Implement recurring tasks:

- Add repeat field: none, daily, weekdays, weekly, monthly.
- Show repeat pill on task cards only when enabled.
- On completing a recurring task, reschedule it to the next occurrence instead of moving it to done.
- Recalculate `dueAtUtc` and local notification after rescheduling.

## Low-Token Workflow

- Avoid reading full `index.html`; use `rg` and small `Select-String -Context` windows.
- Avoid full Gradle logs; run build only after a batch of changes.
- Build/send APK only after a completed milestone, not after every tiny UI edit.
- Commit once per milestone.
- Prefer editing small sections with `apply_patch`.
