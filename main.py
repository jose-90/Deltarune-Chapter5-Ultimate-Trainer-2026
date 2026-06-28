"""
Entry point for Deltarune Chapter 5 Ultimate Trainer.
"""
import asyncio
import threading
from src.utils import setup_logging
from src.memory import MemoryManager
from src.trainer import Trainer
from src.gui import App
from src.web_dashboard import WebDashboard
from src.config import config

main_loop: asyncio.AbstractEventLoop = None

async def run_web(dashboard: WebDashboard):
    await dashboard.start()

def start_asyncio():
    global main_loop
    main_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(main_loop)
    memory = MemoryManager()
    trainer = Trainer(memory)
    dashboard = WebDashboard(trainer, port=config.web_dashboard_port)
    main_loop.create_task(run_web(dashboard))
    main_loop.run_forever()

def main():
    setup_logging()
    loop_thread = threading.Thread(target=start_asyncio, daemon=True)
    loop_thread.start()

    while main_loop is None:
        pass

    memory = MemoryManager()
    trainer = Trainer(memory)
    app = App(trainer, memory)
    app.setup_tray()
    app.mainloop()

if __name__ == "__main__":
    main()
