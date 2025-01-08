from homeassistant.components.switch import SwitchEntity
from .web_requests import turn_on, turn_off

class PowerSwitch(SwitchEntity):
    def __init__(self, timer_entity):
        self._state = False
        self._timer_entity = timer_entity

    @property
    def is_on(self):
        return self._state

    async def async_turn_on(self, **kwargs):
        result = turn_on()
        if result:
            self._state = True
            await self._timer_entity.start_timer()
        else:
            self._state = False

    def turn_off(self, **kwargs):
        result = turn_off()
        if result:
            self._state = False
            if self._timer_entity.is_timer_running():
                self._timer_entity.stop_timer()
        else:
            self._state = True
