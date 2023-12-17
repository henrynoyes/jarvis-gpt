from gpiozero import LED
import apa102
import time
import numpy as np

driver = apa102.APA102(num_led=12)
power = LED(5)
power.on()


col = (0,20)
for i in range(36):
    n = (i//12 + 1) % 2 
    i %= 12
    driver.set_pixel(i, 0, col[n], col[n])
    driver.show()
    time.sleep(0.3/(i+1) + 0.05*n)

# for i in range(12):
#     driver.set_pixel(i, 0, 10, 10)
#     driver.show()
#     time.sleep(0.3/(i+1) + 0.05)
# 
# driver.clear_strip()
# 
# for i in 3*(0,1):
#     for pix in np.arange(i,13,2,dtype=int):
#         driver.set_pixel(pix, 0, 10, 10)
#     
#     driver.show()
#     time.sleep(0.3)
#     driver.clear_strip()

# patterns = 4*[np.arange(12, dtype=int)]
# rng = np.random.default_rng()
# 
# for pidx, pattern in enumerate(patterns):
#     rng.shuffle(pattern)
#     if pidx % 2 == 0:
#         col = 10
#     else:
#         col = 0
#     for idx, pix in enumerate(pattern):
#         driver.set_pixel(pix, 0, col, col)
#         time.sleep(0.8/(idx+1))
#         driver.show()
#     time.sleep(0.1)