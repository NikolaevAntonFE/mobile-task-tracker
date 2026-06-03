from __future__ import annotations

import json
import mimetypes
import os
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
TASKS_FILE = DATA_DIR / "tasks.json"
CHECK_EVERY_SECONDS = 20
DEFAULT_SOURCE_OFFSET_MINUTES = 7 * 60
CATEGORY_TITLES = {
    "Работа": "Рабочее напоминание",
    "Жизнь": "Напоминание по жизни",
    "Напоминалка": "Напоминалка",
}


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def telegram_settings() -> tuple[str, str]:
    env = read_env_file(ROOT / ".env")
    token = os.environ.get("TELEGRAM_BOT_TOKEN") or env.get("TELEGRAM_BOT_TOKEN") or ""
    chat_id = os.environ.get("TELEGRAM_CHAT_ID") or env.get("TELEGRAM_CHAT_ID") or ""
    return token, chat_id


def load_tasks() -> list[dict]:
    if not TASKS_FILE.exists():
        return []
    try:
        data = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_tasks(tasks: list[dict]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    TASKS_FILE.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json_body(handler: BaseHTTPRequestHandler):
    length = int(handler.headers.get("Content-Length", "0"))
    if length <= 0:
        return None
    return json.loads(handler.rfile.read(length).decode("utf-8"))


def now_stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def task_response(task: dict | None, status: int = 200) -> tuple[dict, int]:
    if task is None:
        return {"ok": False, "error": "task not found"}, 404
    return {"ok": True, "task": task}, status


def telegram_request(method: str, data: dict | None = None, timeout: int = 15) -> dict | None:
    token, _chat_id = telegram_settings()
    if not token:
        return None
    url = f"https://api.telegram.org/bot{token}/{method}"
    payload = urllib.parse.urlencode(data or {}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
            return body if isinstance(body, dict) else None
    except Exception as exc:
        log(f"telegram {method} failed: {exc}")
        return None


def send_telegram(text: str) -> dict | None:
    token, chat_id = telegram_settings()
    if not token or not chat_id:
        return None
    body = telegram_request("sendMessage", {"chat_id": chat_id, "text": text})
    if not body or not body.get("ok"):
        return None
    result = body.get("result")
    return result if isinstance(result, dict) else None


def send_test_reminder() -> bool:
    stamp = datetime.now().isoformat(timespec="seconds")
    return send_telegram(f"Тест task tracker\nВремя сервера: {stamp}") is not None


def reminder_title(task: dict) -> str:
    return CATEGORY_TITLES.get(task.get("project") or "", "Напоминалка")


def reminder_time_label(due: str, due_time: str) -> str:
    parts = due.split("-")
    day_month = f"{parts[2]}.{parts[1]}" if len(parts) == 3 else due
    return f"{day_month} {due_time}".strip()


def due_at_from_task(task: dict) -> datetime | None:
    due_at_utc = (task.get("dueAtUtc") or "").strip()
    if due_at_utc:
        try:
            return datetime.fromisoformat(due_at_utc.replace("Z", "+00:00")).astimezone(timezone.utc)
        except ValueError:
            pass

    due = (task.get("due") or "").strip()
    due_time = (task.get("time") or "").strip()
    if not due or not due_time:
        return None
    try:
        offset_minutes = int(task.get("sourceOffsetMinutes") or DEFAULT_SOURCE_OFFSET_MINUTES)
        tz = timezone.utc if offset_minutes == 0 else timezone(timedelta(minutes=offset_minutes))
        return datetime.strptime(f"{due} {due_time}", "%Y-%m-%d %H:%M").replace(tzinfo=tz).astimezone(timezone.utc)
    except ValueError:
        return None


def log(message: str) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().isoformat(timespec="seconds")
    with (DATA_DIR / "server.log").open("a", encoding="utf-8") as fh:
        fh.write(f"{stamp} {message}\n")


def reminder_loop() -> None:
    while True:
        try:
            now = datetime.now(timezone.utc)
            tasks = load_tasks()
            changed = False
            for task in tasks:
                if task.get("done") or task.get("notifiedAt"):
                    continue
                due_at = due_at_from_task(task)
                if due_at is None:
                    continue
                if due_at <= now:
                    due = (task.get("due") or "").strip()
                    due_time = (task.get("time") or "").strip()
                    message = (
                        f"{reminder_title(task)}: {task.get('text', '').strip()}\n"
                        f"Время: {reminder_time_label(due, due_time)}"
                    )
                    sent = send_telegram(message)
                    if sent:
                        task["notifiedAt"] = now.isoformat(timespec="seconds")
                        task["telegramChatId"] = sent.get("chat", {}).get("id")
                        task["telegramMessageId"] = sent.get("message_id")
                        changed = True
                        log(f"sent reminder for task {task.get('id')} message {task.get('telegramMessageId')}")
            if changed:
                save_tasks(tasks)
        except Exception as exc:
            log(f"reminder loop error: {exc}")
        time.sleep(CHECK_EVERY_SECONDS)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        log(format % args)

    def send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def send_json(self, data, status: int = 200) -> None:
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_cors_headers()
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/tasks":
            self.send_json(load_tasks())
            return
        if parsed.path == "/api/status":
            token, chat_id = telegram_settings()
            self.send_json({
                "telegramToken": bool(token),
                "chatId": bool(chat_id),
                "tasks": len(load_tasks()),
                "telegramMode": "send-only",
            })
            return
        path = parsed.path.strip("/") or "index.html"
        target = (ROOT / path).resolve()
        if not str(target).startswith(str(ROOT)) or not target.exists() or target.is_dir():
            self.send_error(404)
            return
        content = target.read_bytes()
        mime = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/test-reminder":
            ok = send_test_reminder()
            self.send_json({"ok": ok})
            return
        if parsed.path != "/api/tasks":
            self.send_error(404)
            return
        try:
            data = read_json_body(self)
            if not isinstance(data, list):
                if not isinstance(data, dict):
                    raise ValueError("expected task object or list")
                tasks = load_tasks()
                task_id = data.get("id")
                if not task_id:
                    raise ValueError("task id is required")
                if any(task.get("id") == task_id for task in tasks):
                    raise ValueError("task already exists")
                task = {**data}
                stamp = now_stamp()
                task.setdefault("createdAt", stamp)
                task["updatedAt"] = task.get("updatedAt") or stamp
                tasks.insert(0, task)
                save_tasks(tasks)
                self.send_json({"ok": True, "task": task, "count": len(tasks)}, status=201)
                return
            save_tasks(data)
            self.send_json({"ok": True, "count": len(data)})
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=400)

    def do_PATCH(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        prefix = "/api/tasks/"
        if not parsed.path.startswith(prefix):
            self.send_error(404)
            return
        task_id = urllib.parse.unquote(parsed.path[len(prefix):])
        try:
            patch = read_json_body(self)
            if not isinstance(patch, dict):
                raise ValueError("expected patch object")
            tasks = load_tasks()
            updated = None
            for index, task in enumerate(tasks):
                if task.get("id") == task_id:
                    updated = {**task, **patch, "id": task_id, "updatedAt": patch.get("updatedAt") or now_stamp()}
                    tasks[index] = updated
                    break
            body, status = task_response(updated)
            if updated is not None:
                save_tasks(tasks)
                body["count"] = len(tasks)
            self.send_json(body, status=status)
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=400)

    def do_DELETE(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        prefix = "/api/tasks/"
        if not parsed.path.startswith(prefix):
            self.send_error(404)
            return
        task_id = urllib.parse.unquote(parsed.path[len(prefix):])
        tasks = load_tasks()
        next_tasks = [task for task in tasks if task.get("id") != task_id]
        if len(next_tasks) == len(tasks):
            self.send_json({"ok": False, "error": "task not found"}, status=404)
            return
        save_tasks(next_tasks)
        self.send_json({"ok": True, "id": task_id, "count": len(next_tasks)})


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    threading.Thread(target=reminder_loop, daemon=True).start()
    log("telegram mode send-only")
    server = ThreadingHTTPServer(("0.0.0.0", 8787), Handler)
    log("server started on 0.0.0.0:8787")
    server.serve_forever()


if __name__ == "__main__":
    main()
