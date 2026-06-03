# Mobile Task Tracker

Personal task tracker with a mobile-first web UI, Android wrapper, Telegram reminders, and native Android local notifications.

## Current Capabilities

- Quick task creation
- Open / overdue / done views
- Inline calendar and time picker
- Native Android local notifications
- Telegram send-only reminders from the Python server
- LAN sync between Android app and local Python server
- Item-level task API for safer updates

## Run Server

```powershell
python server.py
```

Local web UI:

```text
http://127.0.0.1:8787/
```

Phone / Android API target on the current network:

```text
http://192.168.100.25:8787
```

## Android

Install dependencies:

```powershell
npm install
```

Sync Capacitor:

```powershell
npx cap sync android
```

Build debug APK:

```powershell
npm run android:debug
```

APK output:

```text
android/app/build/outputs/apk/debug/app-debug.apk
```

## Notes

- `data/` is intentionally ignored because it contains local task data and logs.
- APK files and Android build outputs are intentionally ignored.
- The Android app uses the bundled `www/` UI and talks to the Python server over LAN.
- Telegram mode must stay send-only; do not add bot polling or `getUpdates` to this project.
