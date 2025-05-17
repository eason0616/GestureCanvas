import pyautogui
import time
import sys

# 設置 pyautogui 的安全設置
pyautogui.FAILSAFE = False  # 將滑鼠移動到螢幕左上角會觸發 FailSafe
pyautogui.PAUSE = 0  # 每次操作間隔 0.1 秒

class MouseController:
    def __init__(self):
        # 獲取螢幕尺寸
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"Screen size: {self.screen_width}x{self.screen_height}")

    def move_to(self, x, y, duration=0.2):
        """
        移動滑鼠到指定位置
        x, y: 目標座標
        duration: 移動持續時間（秒）
        """
        try:
            # 確保座標在螢幕範圍內
            x = max(0, min(x, self.screen_width))
            y = max(0, min(y, self.screen_height))
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            print(f"Error moving mouse: {e}")
            return False

    def move_relative(self, dx, dy, duration=0.03):
        """
        相對當前位置移動滑鼠
        dx, dy: 相對移動距離
        duration: 移動持續時間（秒）
        """
        try:
            pyautogui.moveRel(dx, dy, duration=duration)
            return True
        except Exception as e:
            print(f"Error moving mouse: {e}")
            return False

    def get_position(self):
        """
        獲取當前滑鼠位置
        """
        try:
            x, y = pyautogui.position()
            return x, y
        except Exception as e:
            print(f"Error getting mouse position: {e}")
            return None

    def click(self, x=None, y=None, button='left'):
        """
        在指定位置點擊滑鼠
        x, y: 點擊位置（如果不指定則在當前位置點擊）
        button: 'left', 'right', 'middle'
        """
        try:
            if x is not None and y is not None:
                self.move_to(x, y)
            pyautogui.click(button=button)
            return True
        except Exception as e:
            print(f"Error clicking mouse: {e}")
            return False

    def drag_to(self, x, y, duration=0.2, button='left'):
        """
        拖曳滑鼠到指定位置
        x, y: 目標座標
        duration: 拖曳持續時間（秒）
        button: 使用的滑鼠按鍵
        """
        try:
            pyautogui.dragTo(x, y, duration=duration, button=button)
            return True
        except Exception as e:
            print(f"Error dragging mouse: {e}")
            return False
        
    def release(self, button='left'):
        """
        釋放滑鼠按鍵
        button: 'left', 'right', 'middle'
        """
        try:
            pyautogui.mouseUp(button=button)
            return True
        except Exception as e:
            print(f"Error releasing mouse: {e}")
            return False

def demo():
    """
    展示所有滑鼠控制功能的示例
    """
    controller = MouseController()
    
    # 顯示當前位置
    print("Current position:", controller.get_position())
    
    # 移動到螢幕中心
    center_x = controller.screen_width // 2
    center_y = controller.screen_height // 2
    print(f"Moving to center: {center_x}, {center_y}")
    controller.move_to(center_x, center_y)
    time.sleep(1)
    
    # 相對移動
    print("Moving relative: +100, +100")
    controller.move_relative(100, 100)
    time.sleep(1)
    
    # 點擊
    print("Clicking at current position")
    controller.click()
    time.sleep(1)
    
    # 拖曳
    print("Dragging to new position")
    controller.drag_to(center_x + 200, center_y + 200)

if __name__ == "__main__":
    demo()