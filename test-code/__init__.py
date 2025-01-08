###The Garo G-CTRL Integration"""
import logging
from homeassistant.helpers.entity import entity
from .config_flow import ConfigFlow

from .switch import PowerSwitch
from .timer import PowerTimeout

PLATFORMS = [
    PowerSwitch.SWITCH,
    PowerTimeout.TIMER,
]