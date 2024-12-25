import tkinter as tk
import threading
import queue
import time
import json
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer
import os
import platform


class VoiceSubtitleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("实时语音字幕")

        # 设置窗口属性：始终置顶，无边框，完全透明
        if platform.system() == 'Darwin':  # macOS
            self.root.attributes('-topmost', 1)
            self.root.attributes('-alpha', 1.0)
            self.root.attributes('-transparent', True)
            self.root.configure(bg='black')  # 使用黑色背景
            self.root.wm_attributes('-transparent', True)
            self.root.update_idletasks()
            self.root.lift()
        else:  # Windows 和其他系统
            self.root.attributes('-topmost', True)
            self.root.attributes('-alpha', 1.0)
            self.root.configure(bg='black')

        self.root.overrideredirect(True)  # 无边框模式

        # 设置窗口大小和位置
        self.window_width = 800
        self.window_height = 100
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = screen_height - self.window_height - 100
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

        # 创建文字标签
        self.text_label = tk.Label(
            root,
            text="",  # 初始时不显示文字
            font=("Arial", 24, "bold"),
            fg="white",
            bg='black',  # 使用黑色背景
            wraplength=780,
            highlightthickness=0,
            borderwidth=0
        )
        self.text_label.pack(expand=True, fill='both', padx=10)

        # 添加拖动功能
        self.text_label.bind('<Button-1>', self.start_move)
        self.text_label.bind('<B1-Motion>', self.on_move)

        # 添加右键点击退出功能
        self.text_label.bind('<Button-3>', lambda e: self.on_closing())

        self.is_running = True
        self.audio_queue = queue.Queue()
        self.partial_result = ""
        self.last_voice_time = time.time()

        try:
            # 初始化Vosk模型
            print("正在加载语音识别模型...")
            model_path = "../vosk-model-cn-0.22"
            if not os.path.exists(model_path):
                model_path = "../vosk-model-small-cn-0.22"
                print("未找到中型模型，使用小型模型")

            if not os.path.exists(model_path):
                print(f"错误：找不到模型文件夹 {model_path}")
                self.update_subtitle(f"错误：找不到模型文件夹 {model_path}")
                return

            print(f"使用模型: {model_path}")
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
            self.recognizer.SetMaxAlternatives(0)
            self.recognizer.SetWords(True)
            print("模型加载完成")

            # 获取可用的音频设备
            devices = sd.query_devices()
            print("可用的音频设备：")
            for i, device in enumerate(devices):
                print(f"{i}: {device['name']}")

            # 使用默认输入设备
            default_input = sd.query_devices(kind='input')
            print(f"使用默认输入设备: {default_input['name']}")

            # 启动音频处理线程
            self.audio_thread = threading.Thread(target=self.process_audio)
            self.audio_thread.daemon = True
            self.audio_thread.start()

            # 启动识别线程
            self.recognition_thread = threading.Thread(target=self.recognize_speech)
            self.recognition_thread.daemon = True
            self.recognition_thread.start()

        except Exception as e:
            print(f"初始化错误: {str(e)}")
            self.update_subtitle(f"初始化失败: {str(e)}")
            return

    def start_move(self, event):
        """开始拖动窗口"""
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        """处理窗口拖动"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def audio_callback(self, indata, frames, time, status):
        """音频回调函数"""
        if status:
            print(status)
        self.audio_queue.put(bytes(indata))

    def process_audio(self):
        """处理音频输入"""
        try:
            with sd.RawInputStream(samplerate=16000, channels=1, dtype='int16',
                                   blocksize=4000,
                                   device=None,
                                   callback=self.audio_callback):
                print("开始录音...")
                while self.is_running:
                    time.sleep(0.05)
                    self.root.after(0, self.fade_out_text)
        except Exception as e:
            print(f"音频处理错误: {str(e)}")
            self.root.after(0, self.update_subtitle, f"音频处理错误: {str(e)}")

    def recognize_speech(self):
        """语音识别处理"""
        print("开始识别...")

        while self.is_running:
            try:
                audio_data = self.audio_queue.get(timeout=0.5)
                if len(audio_data) == 0:
                    continue

                if self.recognizer.AcceptWaveform(audio_data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        print(f"最终结果: {text}")
                        self.last_voice_time = time.time()
                        self.root.after(0, self.update_subtitle, text)
                else:
                    partial = json.loads(self.recognizer.PartialResult())
                    partial_text = partial.get("partial", "").strip()
                    if partial_text and partial_text != self.partial_result:
                        self.partial_result = partial_text
                        print(f"部分结果: {partial_text}")
                        self.last_voice_time = time.time()
                        self.root.after(0, self.update_subtitle, partial_text)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"识别错误: {str(e)}")
                time.sleep(0.1)

    def fade_out_text(self):
        """文字淡出效果"""
        try:
            if time.time() - self.last_voice_time > 3:  # 3秒无输入后开始淡化
                current_color = self.text_label.cget('fg')
                if current_color == 'white':  # 如果是完全不透明
                    self.text_label.configure(fg='#FFFFFF')  # 设置初始颜色
                else:
                    # 提取当前颜色值
                    color = current_color.lstrip('#')
                    if len(color) == 6:  # 确保是有效的颜色值
                        # 降低不透明度
                        new_alpha = max(0, int(color[0:2], 16) - 15)
                        if new_alpha > 0:  # 如果还没有完全透明
                            new_color = f'#{new_alpha:02x}{new_alpha:02x}{new_alpha:02x}'
                            self.text_label.configure(fg=new_color)
                            self.root.after(50, self.fade_out_text)  # 继续淡化
                        else:
                            # 完全透明时清空文字
                            self.text_label.config(text="")
                            self.text_label.update()
        except Exception as e:
            print(f"淡化效果错误: {str(e)}")

    def update_subtitle(self, text):
        """更新字幕文本"""
        if not text:
            return
        self.text_label.config(text=text)
        self.text_label.configure(fg='white')
        self.text_label.update()
        self.last_voice_time = time.time()

    def on_closing(self):
        self.is_running = False
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceSubtitleApp(root)
    root.mainloop()