import mss
import mss.tools
import numpy as np
import cv2 as cv

monitor = {"top": 0, "left": 0, "width": 800, "height": 600}

# 创建一个 MSS 对象
with mss.mss() as sct:
    while True:
        shot = sct.grab(monitor)
        shot = np.array(shot)
        shotGray = cv.cvtColor(shot, cv.COLOR_BGR2GRAY)
        
        target = cv.cvtColor(cv.imread("images/target.png"), cv.COLOR_BGR2GRAY)
        
        res = cv.matchTemplate(shotGray, target, cv.TM_CCOEFF_NORMED)
        
        locations = np.where(res >= 0.8)
        
        for pt in zip(*locations[::-1]):
            cv.rectangle(shot, pt, (pt[0] + 80, pt[1] + 30), (0, 0, 255), 2)
        
        cv.imshow("DNF", shot)
        key = cv.waitKey(10)
        if key == ord('q'):
            cv.destroyAllWindows()
            break

