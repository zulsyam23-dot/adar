"""Development server with watch mode — `adarpc serve` and `adarpc watch`."""

from __future__ import annotations
import os
import time
import socket
import threading
import mimetypes
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .config import AdarpcConfig
from .build import build

_LIVERELOAD_SCRIPT = """\
<script>
(function() {
    var ws = new WebSocket('ws://' + location.host);
    ws.onmessage = function(e) {
        if (e.data === 'reload') location.reload();
    };
    ws.onclose = function() { setTimeout(arguments.callee, 1000) };
})();
</script>"""


class _DevHandler(BaseHTTPRequestHandler):
    """Routes: /style/* -> output/style/, everything else -> src/."""

    config: AdarpcConfig | None = None

    def do_GET(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0].lstrip("/")
        if path.startswith("style/"):
            file_path = self.config.out_dir / path if self.config else None
        else:
            file_path = self.config.src_dir / path if self.config else None

        if file_path and file_path.is_file():
            self._serve_file(file_path)
        elif file_path and file_path.is_dir():
            index = file_path / "index.html"
            if index.is_file():
                self._serve_file(index, inject_livereload=True)
            else:
                self._send_error(404, "Not found")
        elif file_path and not file_path.suffix:
            html_path = file_path.with_suffix(".html")
            if html_path.is_file():
                self._serve_file(html_path, inject_livereload=True)
            else:
                self._send_error(404, f"Not found: {self.path}")
        else:
            self._send_error(404, f"Not found: {self.path}")

    def _serve_file(self, path: Path, inject_livereload: bool = False):
        try:
            content = path.read_bytes()
            if inject_livereload and path.suffix.lower() == ".html":
                html = content.decode("utf-8")
                if "</body>" in html:
                    html = html.replace("</body>", _LIVERELOAD_SCRIPT + "\n</body>")
                    content = html.encode("utf-8")

            mime, _ = mimetypes.guess_type(str(path))
            if mime is None and path.suffix == ".css":
                mime = "text/css"
            self.send_response(200)
            self.send_header("Content-Type", mime or "application/octet-stream")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except OSError:
            self._send_error(500, "Internal error")

    def _send_error(self, code: int, msg: str):
        self.send_response(code)
        body = f"<h1>{code}</h1><p>{msg}</p>".encode("utf-8")
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"  [{self.command}] {args[0]} {args[1]} {args[2]}")


class _WebSocketServer:
    """Minimal WebSocket server for sending reload signals."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._clients: list[socket.socket] = []
        self._server: socket.socket | None = None

    def start(self):
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((self.host, self.port))
        self._server.listen(5)
        self._server.settimeout(0.5)

        def _accept():
            while True:
                try:
                    client, _addr = self._server.accept()
                    try:
                        self._handle_client(client)
                        self._clients.append(client)
                    except Exception:
                        self._remove_client(client)
                except socket.timeout:
                    continue
                except OSError:
                    break

        thread = threading.Thread(target=_accept, daemon=True)
        thread.start()

    def _handle_client(self, client: socket.socket):
        try:
            data = client.recv(4096)
            if data:
                key = None
                for line in data.decode("utf-8", errors="ignore").split("\r\n"):
                    if line.startswith("Sec-WebSocket-Key:"):
                        key = line.split(":", 1)[1].strip()
                        break
                if key:
                    import hashlib, base64
                    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
                    accept = base64.b64encode(
                        hashlib.sha1((key + GUID).encode()).digest()
                    ).decode()
                    handshake = (
                        "HTTP/1.1 101 Switching Protocols\r\n"
                        "Upgrade: websocket\r\n"
                        "Connection: Upgrade\r\n"
                        f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
                    )
                    client.sendall(handshake.encode())
        except Exception:
            self._remove_client(client)

    def broadcast(self, message: str):
        frame = self._encode_frame(message)
        dead = []
        for client in self._clients:
            try:
                client.sendall(frame)
            except Exception:
                dead.append(client)
        for c in dead:
            self._remove_client(c)

    def _remove_client(self, client: socket.socket):
        try:
            self._clients.remove(client)
            client.close()
        except (ValueError, OSError):
            pass

    @staticmethod
    def _encode_frame(text: str) -> bytes:
        data = text.encode("utf-8")
        length = len(data)
        if length < 126:
            return bytes([0x81, length]) + data
        return bytes([0x81, 126, length >> 8, length & 0xFF]) + data

    def stop(self):
        if self._server:
            self._server.close()


def _watch_directory(directory: Path, callback):
    """Watch directory for file changes and call callback."""
    watched: dict[Path, float] = {}
    for f in directory.rglob("*.adar"):
        try:
            watched[f] = f.stat().st_mtime
        except OSError:
            pass

    while True:
        time.sleep(0.5)
        changed = False
        current_files = set()
        try:
            current_files = set(directory.rglob("*.adar"))
        except OSError:
            pass

        for f in current_files:
            try:
                mtime = f.stat().st_mtime
                if f not in watched or mtime > watched[f]:
                    watched[f] = mtime
                    changed = True
            except OSError:
                pass

        for f in list(watched.keys()):
            if f not in current_files:
                del watched[f]

        if changed:
            callback()


def serve(config: AdarpcConfig):
    """Start a development server with live reload.
    Routes: /style/* -> output/style/, everything else -> src/.
    """
    config.out_dir.mkdir(parents=True, exist_ok=True)

    print("  Building project...")
    build(config)

    ws_port = config.dev.port + 1
    ws = _WebSocketServer("0.0.0.0", ws_port)
    ws.start()

    _DevHandler.config = config
    httpd = ThreadingHTTPServer(("0.0.0.0", config.dev.port), _DevHandler)

    print(f"\n  Dev server: http://localhost:{config.dev.port}")
    print(f"  HTML: {config.src_dir}")
    print(f"  CSS:  {config.out_dir / 'style'}")
    print(f"  Watching: {config.src_dir}")
    print("  Press Ctrl+C to stop\n")

    if config.dev.watch:
        def on_change():
            print(f"\n  Change detected, rebuilding...")
            build(config)
            ws.broadcast("reload")
            print(f"  Watching {config.src_dir} for changes...")

        watch_thread = threading.Thread(
            target=_watch_directory,
            args=(config.src_dir, on_change),
            daemon=True,
        )
        watch_thread.start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        httpd.shutdown()
        ws.stop()


def watch(config: AdarpcConfig):
    """Watch source directory and rebuild on changes."""
    print(f"  Watching {config.src_dir} for changes...")
    print("  Press Ctrl+C to stop\n")

    build(config)

    def on_change():
        print(f"\n  Change detected, rebuilding...")
        build(config)
        print(f"\n  Watching {config.src_dir} for changes...")

    try:
        _watch_directory(config.src_dir, on_change)
    except KeyboardInterrupt:
        print("\n  Stopped.")
