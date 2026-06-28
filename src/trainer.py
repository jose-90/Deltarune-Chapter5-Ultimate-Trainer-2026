"""
Main trainer logic with asyncio loop, hotkeys, and Discord Rich Presence.
"""
import asyncio
import keyboard
import logging
import time
from typing import Dict, Optional
from discordrpc import DiscordRPC
from .memory import MemoryManager
from .offsets import CURRENT_OFFSETS
from .config import config

logger = logging.getLogger(__name__)

class Trainer:
    def __init__(self, memory: MemoryManager):
        self.memory = memory
        self.active_cheats: Dict[str, bool] = {
            "infinite_hp": False,
            "max_stats": False,
            "unlimited_items": False,
            "infinite_gold": False,
            "one_hit_kill": False,
            "speed_hack": False,
            "freeze_timer": False,
            "unlock_all": False,
        }
        self.loop_task: Optional[asyncio.Task] = None
        self.rpc: Optional[DiscordRPC] = None
        self.speed_mult = 1.0
        self.running = False

    async def start_loop(self):
        if self.running:
            return
        self.running = True
        if config.enable_discord_rp:
            self.rpc = DiscordRPC("1023456789123456789")
            await self.rpc.connect()
        logger.info("Trainer loop started.")
        self.loop_task = asyncio.create_task(self._cheat_loop())

    async def _cheat_loop(self):
        while self.running:
            if self.memory.is_attached():
                try:
                    base = self.memory.module_base
                    if self.active_cheats.get("infinite_hp"):
                        for i in range(3):
                            hp_addr = base + CURRENT_OFFSETS.hp_current + (i * 0x4)
                            max_addr = base + CURRENT_OFFSETS.hp_max + (i * 0x4)
                            max_val = self.memory.read_int(max_addr)
                            self.memory.write_int(hp_addr, max_val)
                    if self.active_cheats.get("max_stats"):
                        for i in range(3):
                            self.memory.write_int(base + CURRENT_OFFSETS.atk + (i*4), 9999)
                            self.memory.write_int(base + CURRENT_OFFSETS.def_ + (i*4), 9999)
                            self.memory.write_int(base + CURRENT_OFFSETS.magic + (i*4), 9999)
                    if self.active_cheats.get("infinite_gold"):
                        self.memory.write_int(base + CURRENT_OFFSETS.gold, 9999999)
                    if self.active_cheats.get("unlimited_items"):
                        # Placeholder: actual implementation would iterate inventory slots
                        pass
                except Exception as e:
                    logger.error(f"Cheat loop error: {e}")
                await asyncio.sleep(config.memory_scan_interval)
            else:
                logger.warning("Game process not attached, waiting...")
                await asyncio.sleep(2)

    def stop_loop(self):
        self.running = False
        if self.loop_task:
            self.loop_task.cancel()
        if self.rpc:
            asyncio.create_task(self.rpc.close())
        logger.info("Trainer loop stopped.")

    def toggle_cheat(self, name: str, state: bool):
        if name in self.active_cheats:
            self.active_cheats[name] = state
            logger.info(f"Cheat '{name}' set to {state}")
            if self.rpc:
                asyncio.create_task(self.rpc.set_activity(state=f"{name} {'ON' if state else 'OFF'}",
                                                          details="Deltarune Chapter 5 Trainer"))

    async def update_discord_presence(self):
        if self.rpc:
            active = [k for k, v in self.active_cheats.items() if v]
            status = ", ".join(active) if active else "No cheats active"
            await self.rpc.set_activity(state=status, details="Deltarune Chapter 5 Trainer")
