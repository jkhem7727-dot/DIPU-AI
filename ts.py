import pyautogui
import time

for i in range(10):   # runs 10 times
    x, y = pyautogui.position()
    print(f"Mouse Position: X={x}, Y={y}")
    time.sleep(1)    # wait 1 second
