# Mobile Task Tracker Handoff

Current web/cache version: v67
Last APK version: v65
Last commit before current checkpoint: 87a14c5 Update handoff for v61 delivery
Repository: https://github.com/NikolaevAntonFE/mobile-task-tracker

## Runtime

- Project path: `C:\Users\User\Documents\Codex\2026-06-04\mobile-task-tracker-handoff-c-users`
- Server: `python server.py`
- Local URL: `http://127.0.0.1:8787/?v=67`
- Android API base in app: `http://192.168.100.25:8787`
- Telegram mode must stay send-only. Do not add polling/getUpdates/webhooks/reactions.
- Secrets are in local `.env`; do not print or commit it.

## Current State

- Android Capacitor app works.
- Local Android notifications work.
- Telegram reminder sending works.
- GitHub remote is configured and pushed.
- APK v65 was built locally: `android/app/build/outputs/apk/debug/app-debug.apk`.
- Current UI tabs: `Сегодня`, `Бессрочные`, `Будущие`, `Закрытые`.
- Recurring tasks are implemented:
  - none, daily, weekdays, weekly, monthly;
  - custom interval (`N дней`, stored as `repeat: "interval"` and `repeatIntervalDays`);
  - recurring completion reschedules `due`, recalculates `dueAtUtc`, clears `notifiedAt`, and keeps the task open.
- Task cards support split actions:
  - card tap opens quick attribute actions (`Отложить`, `Срок`, `Повтор`, `Важность`, `Тип`);
  - `...` opens compact manage actions (`Редактировать`, `Удалить`);
  - date chip opens schedule-only edit;
  - repeat chip opens repeat choice.
- Choice sheets and dialogs close by tapping outside the sheet/backdrop.
- Search auto-collapses when empty and blurred.
- `Сегодня` groups tasks by `Просрочено`, `Утро`, `День`, `Вечер`, `Без времени`.
- Full create/edit dialog is compact mobile-first:
  - type, priority, and repeat use horizontal chips;
  - calendar is collapsible inside the `Дата и время` block;
  - `Весь день` lives in the block header;
  - date, time, and calendar toggle share one compact action row.
- Action sheets were refactored:
  - task title and task meta are shown in the header;
  - quick sheet and manage sheet have different layouts and visual weight;
  - manage sheet is intentionally narrower and more utility-like.
- Task list was polished:
  - rows are card-like instead of bare separators;
  - meta is rendered as chips/badges for date, repeat, type, and high/low priority;
  - completed rows are visually de-emphasized.
- Keyboard/mobile behavior was improved in v66:
  - dialogs react to `visualViewport`;
  - form layout compresses when the keyboard is visible;
  - backdrop tap dismiss works for dialogs/sheets/settings.
- Time selection was changed in v67:
  - manual text input was replaced with a wheel-style scroll picker for hours and minutes;
  - selected time is still stored in `taskTime`;
  - time picker also dismisses on backdrop tap.
- APK v61 was sent to the personal Telegram chat via OpenClaw.

## Main Files

- `index.html`: UI, styles, client state, parser, notifications, API calls.
- `server.py`: HTTP API, task storage, Telegram send-only reminders.
- `sw.js`: service worker cache version.
- `www/`: bundled web assets for Android.
- `android/`: Capacitor Android project.

## Next Product Step

- Build and send a fresh `v67` APK to Telegram for on-device testing.
- Test wheel time picker and keyboard behavior on a real phone.
- After phone feedback, continue only with targeted UX tweaks rather than another broad UI pass.

## Low-Token Workflow

- Avoid reading full `index.html`; use `rg` and small `Select-String -Context` windows.
- Avoid full Gradle logs; run build only after a batch of changes.
- Build/send APK only after a completed milestone, not after every tiny UI edit.
- Commit once per milestone.
- Prefer editing small sections with `apply_patch`.
