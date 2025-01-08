from homeassistant.helpers.event import async_call_later

class PowerTimeout:
    def __init__(self, switch_entity):
        self._switch_entity = switch_entity
        self._timer = None

    async def start_timer(self):
        self._timer = async_call_later(
            self.hass, 120 * 60, self._timer_expired
        )

    def stop_timer(self):
        if self._timer:
            self._timer()
            self._timer = None

    def _timer_expired(self, kwargs):
        self._switch_entity.turn_off()
