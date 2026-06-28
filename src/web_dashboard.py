"""
Lightweight aiohttp web dashboard with websockets for live updates.
"""
from aiohttp import web
import asyncio
import json
from .trainer import Trainer

class WebDashboard:
    def __init__(self, trainer: Trainer, port: int = 4200):
        self.trainer = trainer
        self.port = port
        self.app = web.Application()
        self.websockets = set()
        self.app.router.add_get("/", self.index)
        self.app.router.add_get("/ws", self.websocket_handler)

    async def index(self, request):
        return web.Response(text=self._html(), content_type="text/html")

    def _html(self):
        return """<!DOCTYPE html>
<html>
<head><title>Deltarune Trainer Dashboard</title></head>
<body>
<h1>Trainer Dashboard</h1>
<div id="status">Status: ...</div>
<script>
    const ws = new WebSocket("ws://" + location.host + "/ws");
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        document.getElementById("status").innerText = JSON.stringify(data);
    };
</script>
</body>
</html>"""

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.websockets.add(ws)
        try:
            async for msg in ws:
                pass
        finally:
            self.websockets.remove(ws)
        return ws

    async def broadcast_state(self):
        if not self.websockets:
            return
        state = {"cheats": self.trainer.active_cheats, "attached": self.trainer.memory.is_attached()}
        msg = json.dumps(state)
        for ws in set(self.websockets):
            try:
                await ws.send_str(msg)
            except:
                self.websockets.discard(ws)

    async def start(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", self.port)
        await site.start()
        print(f"Web dashboard running on http://localhost:{self.port}")
