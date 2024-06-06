import time
from datetime import datetime


import os,sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class TimeLogger:
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("开始时间：", current_time)

    def end(self):
        self.end_time = time.time()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("结束时间：", current_time)

    def duration(self):
        if self.start_time and self.end_time:
            total_time = self.end_time - self.start_time
            print(f"总耗时：{total_time:.2f} 秒")
        else:
            print("请先调用 start() 和 end() 方法来记录时间。")



def main():

    print(os.path.dirname())

    # 创建 TimeLogger 实例
    time_logger = TimeLogger()

    # 记录开始时间
    time_logger.start()

    # ...

    # 记录结束时间
    time_logger.end()

    # 打印总耗时
    time_logger.duration()
    
if __name__ == '__main__':
    main()