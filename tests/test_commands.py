"""
QUANTUM//OPS - Command Processing Automated Test Suite
Tests command parser, suggestions, and execution routing.
"""

import pytest
from backend.command_handler import CommandHandler


@pytest.mark.asyncio
async def test_help_command():
    resp = await CommandHandler.process("help")
    assert resp.status == "success"
    assert "help" in resp.command
    assert "QUANTUM//OPS" in resp.output
    assert "cudaq" in resp.output
    assert "qiskit" in resp.output
    assert "nvqlink" in resp.output
    assert "shor" in resp.output


@pytest.mark.asyncio
async def test_init_command():
    resp = await CommandHandler.process("init")
    assert resp.status == "success"
    assert "INITIALIZING" in resp.output
    assert "SYSTEM READY" in resp.output


@pytest.mark.asyncio
async def test_system_info_command():
    resp = await CommandHandler.process("system --info")
    assert resp.status == "success"
    assert "SYSTEM HARDWARE" in resp.output
    assert "CPU" in resp.output


@pytest.mark.asyncio
async def test_unknown_command_with_suggestion():
    resp = await CommandHandler.process("cuda")
    assert resp.status == "error"
    assert "Command not recognized" in resp.output
    # Should suggest cudaq
    assert "cudaq" in resp.output or resp.data.get("suggestion") is not None


@pytest.mark.asyncio
async def test_empty_command():
    resp = await CommandHandler.process("   ")
    assert resp.status == "success"
    assert resp.output == ""


@pytest.mark.asyncio
async def test_clear_command():
    resp = await CommandHandler.process("clear")
    assert resp.status == "success"
    assert resp.data.get("action") == "clear"


@pytest.mark.asyncio
async def test_exit_command():
    resp = await CommandHandler.process("exit")
    assert resp.status == "success"
    assert "TERMINATED" in resp.output

