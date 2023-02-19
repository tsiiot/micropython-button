# Copyright (c) 2023 GeekerBear
# Platform-independent MicroPython code for the button module
# Documentation:
#   https://github.com/tsiiot/micropython-button

import micropython
import utime
        
def _trigger_button(rotary_instance, state, t):
    for listener in rotary_instance._button_listener:
        listener(state, t)
        
def _trigger_dbclick(rotary_instance):
    for listener in rotary_instance._dbclick_listener:
        listener()
       
def _trigger_counter(rotary_instance, count):
    for listener in rotary_instance._counter_listener:
        listener(count)


class Button(object):
    
    BUTTON_PRESS = const(0) # 按钮按下
    BUTTON_RELEASE = const(1) # 按钮释放

    def __init__(self, pin_num, btn_value):
        self._pin_num = pin_num
        self._btn_value = btn_value
        self._btn_press_time = 0
        self._btn_press_count = 0
        self._button_listener = []
        self._dbclick_listener = []
        self._counter_listener = []
        
    def close(self):
        """关闭"""
        self._hal_close()

    def add_button_listener(self, l):
        self._button_listener.append(l)
        
    def remove_button_listener(self, l):
        if l not in self._button_listener:
            raise ValueError('{} is not an installed button_listener'.format(l))
        self._button_listener.remove(l)
        
    def add_counter_listener(self, l):
        self._counter_listener.append(l)
        
    def remove_counter_listener(self, l):
        if l not in self._counter_listener:
            raise ValueError('{} is not an installed counter_listener'.format(l))
        self._counter_listener.remove(l)
        
    def add_dbclick_listener(self, l):
        self._dbclick_listener.append(l)
        
    def remove_dbclick_listener(self, l):
        if l not in self._dbclick_listener:
            raise ValueError('{} is not an installed dbclick_listener'.format(l))
        self._dbclick_listener.remove(l)
        
    def _process_button_pins(self, pin):
        """处理按钮"""
        old_value = self._btn_value
        self._btn_value = self._hal_get_btn_value()
        
        try:
            if old_value != self._btn_value:
                if self._btn_value == BUTTON_PRESS: #按下
                    self._btn_press_time = utime.ticks_ms() #按下的时间
                    self._btn_press_count = self._btn_press_count + 1 #按下计数器累加
                    
                    if len(self._button_listener) != 0:
                        _trigger_button(self, self._pin_num, BUTTON_PRESS, 0)
                        
                    if 'click_callback_func' in dir(self):
                        self.click_callback_func( self._pin_num, BUTTON_PRESS, 0)
                        
                elif self._btn_value == BUTTON_RELEASE: #释放
                    diff_time = utime.ticks_ms() - self._btn_press_time
                    
                    if len(self._button_listener) != 0:
                        _trigger_button(self, self._pin_num, BUTTON_RELEASE, diff_time)
                    
                    if 'click_callback_func' in dir(self):
                        self.click_callback_func(self._pin_num, BUTTON_RELEASE, diff_time)
                else:
                    print('按钮: 未知')
        except:
            pass
        
    def click(self, func):
        """
        单击,在方法上添加@btn.click
        """
        self.click_callback_func = func
        
    def _process_counter_timer(self, t):
        """处理按键连续按下计数器"""
        try:
            if self._btn_press_count > 1 and (utime.ticks_ms() - self._btn_press_time) >= 250:
                if self._btn_press_count > 2 and len(self._counter_listener) != 0:
                    _trigger_counter(self, self._pin_num, self._btn_press_count)
                    
                if self._btn_press_count > 2 and 'counter_callback_func' in dir(self):
                    self.counter_callback_func(self._pin_num, self._btn_press_count)
                
                if self._btn_press_count == 2 and len(self._dbclick_listener) != 0:
                    _trigger_dbclick(self)
                    
                if self._btn_press_count == 2 and 'dbclick_callback_func' in dir(self):
                    self.dbclick_callback_func(self._pin_num)
                
                self._btn_press_count = 0
        except Exception as e:
            print(e)
        
        # 如果计数一次,并且两次按键时间大于200毫秒,将不做连续按键处理
        if self._btn_press_count == 1 and (utime.ticks_ms() - self._btn_press_time) >= 230:
            self._btn_press_count = 0
        
    def counter(self, func):
        """
        按键连续按下计数器@btn.counter
        """
        self.counter_callback_func = func
    
    def dbclick(self, func):
        """
        按键双击,在方法上添加@btn.dbclick
        """
        self.dbclick_callback_func = func

