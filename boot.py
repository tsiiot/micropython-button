import sys
import os
from machine import Pin, I2C, SoftI2C, UART
import uasyncio as asyncio
import utime
from button_irq_rp2 import ButtonIRQ

btn = ButtonIRQ(pin_num_btn=22)

@btn.counter
def counter_callback(pin, count):
    """按键连续按下事件"""
    print('按键: %d 被连续按下 %d 次' % (pin, count))

@btn.click
def click_callback(pin, state, time):
    """按键单击事件"""
    print('按键: %d 动作类型: %s 持续时间: %d' % (pin, ('释放' if state == 1 else '按下'), time))
    
@btn.dbclick
def dbclick_callback(pin):
    """按键双击事件"""
    print('按键: %d 按键双击事件触发' % pin)

async def heartbeat():
    while True:
        await asyncio.sleep_ms(10)

event = asyncio.Event()
async def main():
    asyncio.create_task(heartbeat())
    while True:
        await event.wait()
        #print('result =', r.value())
        event.clear()

try:
    asyncio.run(main())
except (KeyboardInterrupt, Exception) as e:
    print('Exception {} {}\n'.format(type(e).__name__, e))
    btn.close()
finally:
    ret = asyncio.new_event_loop()  # Clear retained uasyncio state

