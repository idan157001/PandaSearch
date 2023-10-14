import pyautogui
import time
time.sleep(3)
while True:
    pyautogui.press('down')
    time.sleep(0.05)
    pyautogui.hotkey('ctrl', 'v', interval = 0.1)
    