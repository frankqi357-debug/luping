# Luping - Screen Recorder Tool 🎬

一个轻量级的跨平台屏幕录制工具，基于Python + PyQt6开发。

## ✨ 功能特性

- 📺 **多种录制模式**：全屏、区域、窗口录制
- 🎬 **多格式支持**：MP4、WebM、AVI等
- 🎵 **音频混音**：系统音频 + 麦克风同时录制
- ⏱️ **实时显示**：录制时长和帧率显示
- ⚙️ **灵活配置**：FPS、分辨率、质量可调
- 💾 **配置保存**：自动保存用户偏好设置
- 📝 **日志系统**：完整的调试日志记录

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行程序
```bash
python src/main.py
```

## 📁 项目结构

```
src/
├── main.py                          # 程序入口
├── ui/
│   ├── main_window.py              # 主窗口UI
│   ├── region_selector.py          # 区域选择工具
│   └── settings_dialog.py          # 设置对话框
├── core/
│   ├── screen_capture.py           # 屏幕捕获模块
│   ├── audio_capture.py            # 音频捕获模块
│   └── video_encoder.py            # 视频编码模块
└── utils/
    ├── config.py                   # 配置管理
    └── logger.py                   # 日志系统
```

## 🛠️ 技术栈

- **UI框架**：PyQt6
- **屏幕捕获**：MSS + OpenCV
- **音频处理**：PyAudio + SoundDevice
- **视频编码**：OpenCV VideoWriter

## 📋 开发计划

### Phase 1: MVP
- [x] UI界面设计
- [x] 基础屏幕捕获
- [x] 视频编码导出
- [ ] 测试和优化

### Phase 2: 增强功能
- [ ] 区域选择预览
- [ ] 音频混音实现
- [ ] 快捷键支持

### Phase 3: 高级功能
- [ ] 光标样式选项
- [ ] 水印/文字叠加
- [ ] 录制历史管理
- [ ] 打包为可执行文件

## 🔧 常见问题

**Q: 如何修改录制质量?**
A: 在设置对话框中调整"质量"滑块（1-100）

**Q: 支持哪些输出格式?**
A: 支持MP4、WebM、AVI等常见格式

**Q: 可以录制系统音频吗?**
A: 可以，在音频选项中勾选"系统音频"

## 📄 许可证

MIT License

## 👨‍💻 作者

frankqi357-debug
