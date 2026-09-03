"""Explicit state definitions for the PEEXH communication agent."""

from enum import Enum


class AgentState(str, Enum):
    """Lifecycle states of the PEEXH agent."""
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    INTERPRETING = "INTERPRETING"
    DECIDING = "DECIDING"
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
    CONFIRMED = "CONFIRMED"
