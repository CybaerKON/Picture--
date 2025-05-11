# Picture--
An AI-powered image compression tool with a GUI, capable of compressing images to within a specified file size, adjusting images to a target resolution, or achieving both objectives simultaneously.
一个借助AI创建的、有GUI的图片压缩工具，可将图片压缩至指定尺寸之内，也可以将图片压缩至指定分辨率，亦或二者同时。

一个基于Python的图像压缩工具，提供图形界面，支持批量处理、分辨率调整和多种保存选项。

## 功能特性

- 🖼️ 支持多种格式：JPEG/PNG/BMP/GIF/WEBP
- 📁 批量选择图片文件
- ⚙️ 灵活压缩设置：
  - 自定义目标文件大小（支持B/KB/MB/GB单位）
  - 调整输出分辨率
- 💾 多种保存模式：
  - 替换原文件
  - 另存为新文件
- 🔄 智能重名处理：
  - 自动重命名
  - 覆盖确认
  - 手动选择
- 📊 实时进度显示
- ⏹️ 支持中断操作
- 📂 完成后自动打开文件夹
- 📝 错误日志记录

# 基础环境要求
Python 3.6+ (内置tkinter库)

# 第三方库安装指令
pip install pillow==10.3.0  # 图像处理核心库

# 完整依赖清单
'''
Package    Version
-------    -------
Pillow    10.3.0   # 提供Image/ImageOps模块
tkinter    内置     # GUI框架
os         内置     # 文件系统操作
shutil     内置     # 文件操作
threading  内置     # 多线程支持
math       内置     # 数学计算
datetime   内置     # 时间戳功能
'''

# 验证安装命令
python -c "from PIL import Image; print(Image.__version__)"  # 应输出10.3.0

# 补充说明：
1. 不需要额外数据库，所有数据存储在文件系统中
2. Tkinter为Python标准库，无需单独安装
3. 错误日志存储在项目根目录的compression_errors.log

- Python 3.6+
- Pillow 8.0+
- Tkinter（通常随Python安装）


