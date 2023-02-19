# Copyright (c) 2023 GeekerBear
# ESP8266/ESP32 implementation
# Documentation:
#   https://github.com/tsiiot/micropython-button

from machine import Pin, Timer
from button import Button
from sys import platform

_esp8266_deny_pins = [16]


class ButtonIRQ(Button):

    def __init__(
        self,
        pin_num_btn,
        pull_up=False
    ):

        if platform == 'esp8266':
            if pin_num_btn in _esp8266_deny_pins:
                raise ValueError(
                    '%s: Pin %d not allowed. Not Available for Interrupt: %s' %
                    (platform, pin_num_btn, _esp8266_deny_pins))

        if pull_up == True:
            self._pin_btn = Pin(pin_num_btn, Pin.IN, Pin.PULL_UP)
        else:
            self._pin_btn = Pin(pin_num_btn, Pin.IN)
            
        super().__init__(pin_num_btn, self._pin_btn.value())
        
        self._counter_timer = Timer(1)

        self._enable_btn_irq(self._process_button_pins)
        self._enable_counter_timer(self._process_counter_timer)
    
    def _enable_btn_irq(self, callback=None):
        self._pin_btn.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
            handler=callback)
    
    def _enable_counter_timer(self, callback=None):
        self._counter_timer.init(period=100, mode=Timer.PERIODIC, callback=callback)
        
    def _disable_btn_irq(self):
        self._pin_btn.irq(handler=None)
        
    def _disable_counter_timer(self):
        self._counter_timer.deinit()
    
    def _hal_get_btn_value(self):
        return self._pin_btn.value()

    def _hal_enable_irq(self):
        self._enable_btn_irq(self._process_button_pins)
        self._enable_counter_timer(self._process_counter_timer)

    def _hal_disable_irq(self):
        self._disable_btn_irq()
        self._disable_counter_timer()

    def _hal_close(self):
        self._hal_disable_irq()

