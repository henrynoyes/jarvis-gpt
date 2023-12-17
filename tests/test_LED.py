from gpiozero import LED
import apa102
import time

driver = apa102.APA102(num_led=12)
power = LED(5)
power.on()

for i in range(12):
    driver.set_pixel(i, 10, 100, 10)
    driver.show()
    time.sleep(0.66)
