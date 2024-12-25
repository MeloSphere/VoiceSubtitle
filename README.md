# 实时语音字幕程序

这是一个基于 Python 开发的实时语音字幕显示程序，可以将用户的语音实时转换为屏幕上的字幕文本。支持中文和英文识别，适用于 macOS 和 Windows 系统。

## 功能特点

- 实时语音识别和显示
- 支持中文和英文
- 半透明悬浮窗口
- 自动文字淡出效果
- 支持窗口拖动
- 跨平台支持（MacOS/Windows）

## 安装要求

### 系统要求
- Python 3.7 或更高版本
- macOS 或 Windows 操作系统
- 可用的麦克风设备

### 依赖包
```bash
pip install -r requirements.txt
```

主要依赖：
- vosk：语音识别引擎
- sounddevice：音频输入处理
- numpy：数据处理
- tkinter：图形界面（Python 标准库）

## 安装步骤

1. 克隆或下载项目代码
2. 安装依赖包：
   ```bash
   pip install vosk sounddevice numpy
   ```
3. 下载语音模型（选择其一）：
   ```bash
   # 小型中文模型（约32M）
   wget https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip
   
   # 或下载标准中文模型（约1.2G）
   wget https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip
   ```
4. 解压模型文件到程序目录

## 使用说明

1. 运行程序：
   ```bash
   python voice_subtitle.py
   ```

2. 程序启动后会在屏幕底部显示一个半透明窗口

3. 操作方式：
   - 左键拖动：移动窗口位置
   - 右键点击：退出程序
   - 说话时自动显示文字
   - 停止说话3秒后文字自动淡出

## 配置说明

可以通过修改代码中的以下参数来自定义程序行为：

- `window_width`：窗口宽度（默认800）
- `window_height`：窗口高度（默认100）
- `font`：字体设置（默认"Arial", 24, "bold"）
- 淡出时间：`fade_out_text` 方法中的3秒延迟
- 淡出速度：`fade_out_text` 方法中的渐变参数

## 常见问题

1. 找不到语音模型：
   - 确保模型文件已下载并解压
   - 检查模型文件夹名称是否正确

2. 麦克风不工作：
   - 检查系统麦克风权限设置
   - 确认默认输入设备正确

3. 文字显示问题：
   - 调整窗口位置避免遮挡
   - 检查显示器分辨率设置

## 开发说明

主要类和方法：

- `VoiceSubtitleApp`：主应用类
  - `process_audio`：音频输入处理
  - `recognize_speech`：语音识别
  - `update_subtitle`：更新字幕显示
  - `fade_out_text`：文字淡出效果

## 许可说明

本项目使用的语音识别模型基于 Vosk，遵循 Apache 2.0 许可。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持实时语音识别
- 实现半透明窗口
- 添加文字淡出效果
- 支持窗口拖动

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 致谢

- [Vosk](https://alphacephei.com/vosk/) 提供的语音识别模型
- [sounddevice](https://python-sounddevice.readthedocs.io/) 提供的音频处理支持 