# Mobile Task Tracker Handoff

Current web/cache version: v61
Last APK version: v58
Last commit: 4c71ccd Show editable no due pill
Repository: https://github.com/NikolaevAntonFE/mobile-task-tracker

## Runtime

- Project path: `C:\Users\User\Documents\Codex\2026-06-04\mobile-task-tracker-handoff-c-users`
- Server: `python server.py`
- Local URL: `http://127.0.0.1:8787/?v=61`
- Android API base in app: `http://192.168.100.25:8787`
- Telegram mode must stay send-only. Do not add polling/getUpdates/webhooks/reactions.
- Secrets are in local `.env`; do not print or commit it.

## Current State

- Android Capacitor app works.
- Local Android notifications work.
- Telegram reminder sending works.
- GitHub remote is configured and pushed.
- APK v61 was built locally: `android/app/build/outputs/apk/debug/app-debug.apk`.
- Current UI tabs: `Сегодня`, `Бессрочные`, `Будущие`, `Закрытые`.
- Web/cache v58 includes recurring tasks:
  - none, daily, weekdays, weekly, monthly;
  - custom interval (`N дней`, stored as `repeat: "interval"` and `repeatIntervalDays`);
  - recurring completion reschedules `due`, recalculates `dueAtUtc`, clears `notifiedAt`, and keeps the task open.
- Task cards support inline editing:
  - priority pill opens priority choice;
  - type pill opens type choice;
  - date or `без срока` pill opens date/time editor;
  - card tap opens full edit;
  - `...` opens full edit.
- Choice sheets close by tapping outside the sheet.
- Search auto-collapses when empty and blurred.
- `Сегодня` groups tasks by `Просрочено`, `Утро`, `День`, `Вечер`, `Без времени`.
- Web/cache v59 compacted the full task/reminder creation dialog:
  - type, priority, and repeat controls are horizontal chips;
  - description and calendar are shorter;
  - dialog uses a mobile bottom-sheet cap with sticky header/actions;
  - duplicate dialog/page scroll was removed.
- Web/cache v60 made the calendar inside the full create/edit dialog collapsible:
  - ordinary full create/edit starts with the calendar collapsed;
  - `Дата и время` keeps the date chip and time visible;
  - the calendar opens via the `Календарь` chip;
  - schedule-only date editing opens with the calendar expanded.
- Web/cache v61 compacted the `Дата и время` block:
  - `Весь день` moved into the time panel header;
  - date, time, and calendar toggle now share one compact action row;
  - full create modal collapsed height verified at ~524px with no horizontal overflow;
  - schedule-only date editing still opens expanded and verified with no overflow.
- APK v61 was sent to the personal Telegram chat via OpenClaw.

## Main Files

- `index.html`: UI, styles, client state, parser, notifications, API calls.
- `server.py`: HTTP API, task storage, Telegram send-only reminders.
- `sw.js`: service worker cache version.
- `www/`: bundled web assets for Android.
- `android/`: Capacitor Android project.

## Next Product Step

- Install/test the fresh `v61` APK on phone.
- If recurring UI/reschedule behavior is accepted, commit and optionally send the APK through Telegram.

## Low-Token Workflow

- Avoid reading full `index.html`; use `rg` and small `Select-String -Context` windows.
- Avoid full Gradle logs; run build only after a batch of changes.
- Build/send APK only after a completed milestone, not after every tiny UI edit.
- Commit once per milestone.
- Prefer editing small sections with `apply_patch`.
