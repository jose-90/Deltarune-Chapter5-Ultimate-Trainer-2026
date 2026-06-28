"""
Basic tests for memory manager.
"""
import pytest
from src.memory import MemoryManager

def test_memory_attach_not_running():
    mgr = MemoryManager("nonexistent.exe")
    assert not mgr.attach()
