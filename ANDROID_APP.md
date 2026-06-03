# Android prototype

This is a Capacitor wrapper for the current task tracker server.

Current target server:

```text
http://192.168.100.25:8787
```

The first prototype intentionally loads the existing web app from the LAN server.
That keeps Telegram reminders and task storage on the Python server.

## Requirements

- Node.js and npm
- JDK
- Android Studio / Android SDK

## Commands

```powershell
npm install
npm run android:add
npm run android:sync
npm run android:open
```

For a debug APK:

```powershell
npm run android:debug
```

The APK will be generated under:

```text
android\app\build\outputs\apk\debug\
```

## Notes

- The phone must be on the same Wi-Fi network as the server.
- If the computer IP changes, update `server.url` in `capacitor.config.json`.
- For a production app, move the API/reminder service to a stable backend or implement native/local reminders.
