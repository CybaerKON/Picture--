import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageOps, ImageTk
import os
import threading
import datetime
import shutil
import math

class PictureCompressor:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Picture--")
        self.window.minsize(520, 280)
        self.setup_ui()
        self.files = []
        self.abort_flag = False
        self.duplicate_policy = "ask"

        

    def setup_ui(self):
        # 配置行列权重
        for i in range(4):
            self.window.columnconfigure(i, weight=1)
        self.window.rowconfigure(9, weight=1)

        # 文件选择区域
        ttk.Label(self.window, text="选择图片:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.btn_select = ttk.Button(self.window, text="浏览文件", command=self.select_files)
        self.btn_select.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 文件目录显示
        ttk.Label(self.window, text="文件目录:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.file_dir_entry = ttk.Entry(self.window, state='readonly')
        self.file_dir_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.EW)

        # 目标大小设置
        ttk.Label(self.window, text="目标大小:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.target_size_entry = ttk.Entry(self.window)
        self.target_size_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.size_unit = ttk.Combobox(self.window, values=["B", "KB", "MB", "GB"], state="readonly")
        self.size_unit.current(1)
        self.size_unit.grid(row=1, column=2, padx=5, pady=5, sticky=tk.EW)

        # 分辨率设置
        ttk.Label(self.window, text="宽度 (px):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.width_entry = ttk.Entry(self.window)
        self.width_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        ttk.Label(self.window, text="高度 (px):").grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        self.height_entry = ttk.Entry(self.window)
        self.height_entry.grid(row=2, column=3, padx=5, pady=5, sticky=tk.EW)

        # 保存模式选择
        self.save_mode = tk.StringVar(value="new")
        ttk.Radiobutton(self.window, text="替换原文件", variable=self.save_mode, 
                       value="replace").grid(row=3, column=0, sticky=tk.W)
        ttk.Radiobutton(self.window, text="另存为新文件", variable=self.save_mode,
                       value="new").grid(row=3, column=1, sticky=tk.W)

        # 重名处理策略
        ttk.Label(self.window, text="重名处理:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.dup_policy = ttk.Combobox(self.window, values=["询问", "覆盖", "自动重命名"], state="readonly")
        self.dup_policy.current(0)
        self.dup_policy.grid(row=4, column=1, padx=5, pady=5, sticky=tk.EW)

        # 保存路径选择
        ttk.Button(self.window, text="保存路径", command=self.select_save_path).grid(row=5, column=0, padx=5, pady=5, sticky=tk.EW)
        self.save_path = ttk.Entry(self.window)
        self.save_path.grid(row=5, column=1, columnspan=3, padx=5, pady=5, sticky=tk.EW)

        # 进度条
        self.progress = ttk.Progressbar(self.window, orient="horizontal", mode="determinate")
        self.progress.grid(row=6, column=0, columnspan=4, padx=5, pady=10, sticky=tk.EW)

        # 完成选项
        self.show_folder_var = tk.BooleanVar()
        ttk.Checkbutton(self.window, text="完成后显示文件夹", variable=self.show_folder_var).grid(
            row=7, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

        # 控制按钮
        self.btn_start = ttk.Button(self.window, text="开始压缩", command=self.start_compression)
        self.btn_start.grid(row=7, column=2, padx=5, pady=5, sticky=tk.EW)
        ttk.Button(self.window, text="中断", command=self.cancel).grid(row=7, column=3, padx=5, pady=5, sticky=tk.EW)

    def select_files(self):
        self.files = filedialog.askopenfilenames(filetypes=[
            ("图像文件", "*.jpg;*.jpeg;*.png;*.bmp;*.gif;*.webp"),
            ("所有文件", "*.*")
        ])
        if self.files:
            dir_path = os.path.dirname(self.files[0])
            self.file_dir_entry.config(state='normal')
            self.file_dir_entry.delete(0, tk.END)
            self.file_dir_entry.insert(0, dir_path)
            self.file_dir_entry.config(state='readonly')
    
    def select_save_path(self):
        path = filedialog.askdirectory()
        self.save_path.delete(0, tk.END)
        self.save_path.insert(0, path)

    def handle_duplicate(self, filepath):
        policy = self.dup_policy.get()
        if policy == "自动重命名":
            return "rename"
        elif policy == "覆盖":
            return "overwrite"
        
        choice = messagebox.askyesnocancel(
            "文件冲突",
            f"目标文件已存在:\n{filepath}\n覆盖现有文件？\n(将跳过此文件)",
            icon='warning'
        )
        return "overwrite" if choice else "rename" if choice is None else "skip"

    def get_unique_filename(self, directory, filename):
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(directory, filename)):
            filename = f"{base}_({counter}){ext}"
            counter += 1
        return filename

    def compress_image(self, img_path, save_dir, target_kb):
        temp_file = os.path.join(save_dir, "~temp.jpg")
        try:
            if self.abort_flag:
                return None

            img = Image.open(img_path)
            img = ImageOps.exif_transpose(img)
            original_width, original_height = img.size

            # 处理分辨率调整
            new_size = self.calculate_new_size(original_width, original_height)
            if new_size == (None, None):
                return None
            if new_size:
                new_width, new_height = new_size
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 检查源文件大小
            if target_kb > 0:
                original_size_kb = os.path.getsize(img_path) / 1024
                if original_size_kb <= target_kb:
                    self.log_error(f"源文件大小 ({original_size_kb:.2f}KB) 已小于目标大小，跳过")
                    return None

            quality = 90
            scale_factor = 1.0

            while quality >= 10 and scale_factor >= 0.5:
                if self.abort_flag:
                    return None

                if scale_factor < 1.0:
                    new_size = (int(img.width*scale_factor), int(img.height*scale_factor))
                    resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                else:
                    resized_img = img
                
                resized_img.save(temp_file, quality=quality, optimize=True, progressive=True)
                current_size = os.path.getsize(temp_file) / 1024
                
                if target_kb == 0 or current_size <= target_kb:
                    final_path = self.get_final_path(img_path, save_dir)
                    if not final_path:
                        return None
                    shutil.move(temp_file, final_path)
                    return final_path
                
                quality = max(quality - 5, 10)
                scale_factor = max(scale_factor - 0.1, 0.5)

            return None
        except Exception as e:
            self.log_error(f"压缩失败: {img_path}\n错误信息: {str(e)}")
            return None
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def calculate_new_size(self, original_width, original_height):
        try:
            width_str = self.width_entry.get().strip()
            height_str = self.height_entry.get().strip()
            
            if not width_str and not height_str:
                return None

            # 输入验证
            if width_str:
                input_width = int(width_str)
                if input_width < 10:
                    raise ValueError("宽度不能小于10像素")
            if height_str:
                input_height = int(height_str)
                if input_height < 10:
                    raise ValueError("高度不能小于10像素")

            new_width = int(width_str) if width_str else None
            new_height = int(height_str) if height_str else None

            if new_width and new_height:
                original_ratio = original_width / original_height
                new_ratio = new_width / new_height
                if not math.isclose(original_ratio, new_ratio, rel_tol=1e-3):
                    self.log_error("输入分辨率宽高比与原始图片不一致")
                    return None
                return (new_width, new_height)
            elif new_width:
                return (new_width, int(original_height * (new_width / original_width)))
            elif new_height:
                return (int(original_width * (new_height / original_height)), new_height)
        except ValueError as e:
            self.log_error(str(e))
            return None
        except:
            self.log_error("分辨率输入无效")
            return None

    def get_final_path(self, img_path, save_dir):
        if self.save_mode.get() == "replace":
            final_path = img_path
        else:
            final_name = os.path.basename(img_path)
            final_path = os.path.join(save_dir, final_name)
        
        if os.path.exists(final_path) and final_path != img_path:
            action = self.handle_duplicate(final_path)
            if action == "overwrite":
                os.remove(final_path)
            elif action == "rename":
                final_name = self.get_unique_filename(save_dir, final_name)
                final_path = os.path.join(save_dir, final_name)
            else:
                return None
        return final_path

    def start_compression(self):
        if not self.files or (self.save_mode.get() == "new" and not self.save_path.get()):
            messagebox.showerror("错误", "请先选择文件和保存路径")
            return
        
        # 获取目标大小
        try:
            target_size = self.target_size_entry.get().strip()
            unit = self.size_unit.get()
            target_kb = 0
            if target_size:
                target = float(target_size)
                if unit == "B":
                    target_kb = target / 1024
                elif unit == "KB":
                    target_kb = target
                elif unit == "MB":
                    target_kb = target * 1024
                elif unit == "GB":
                    target_kb = target * 1024 * 1024
                
                # 检查目标大小临界值
                if target_kb > 0 and target_kb < 1:
                    messagebox.showerror("错误", "目标大小不能小于1KB")
                    return
        except:
            messagebox.showerror("错误", "目标大小输入无效")
            return

        # 检查分辨率输入有效性
        try:
            width_str = self.width_entry.get().strip()
            height_str = self.height_entry.get().strip()
            if width_str:
                input_width = int(width_str)
                if input_width < 10:
                    raise ValueError("宽度不能小于10像素")
            if height_str:
                input_height = int(height_str)
                if input_height < 10:
                    raise ValueError("高度不能小于10像素")
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
            return

        self.progress["maximum"] = len(self.files)
        self.progress["value"] = 0
        self.btn_start["state"] = "disabled"
        self.abort_flag = False
        
        threading.Thread(target=self.run_compression, args=(target_kb,), daemon=True).start()

    def run_compression(self, target_kb):
        success = 0
        save_dir = self.save_path.get() if self.save_mode.get() == "new" else os.path.dirname(self.files[0])
        
        for idx, file in enumerate(self.files):
            if self.abort_flag:
                break
            try:
                result = self.compress_image(file, save_dir, target_kb)
                if result:
                    success += 1
                self.progress["value"] = idx + 1
                self.window.update()
            except Exception as e:
                self.log_error(f"处理错误: {file}\n{str(e)}")
        
        self.btn_start["state"] = "normal"
        self.abort_flag = False

        if self.abort_flag:
            messagebox.showinfo("已取消", "操作已被用户取消")
        else:
            messagebox.showinfo("完成", f"成功压缩 {success}/{len(self.files)} 张图片")
            if success > 0 and self.show_folder_var.get():
                try:
                    os.startfile(os.path.abspath(save_dir))
                except Exception as e:
                    self.log_error(f"无法打开文件夹: {save_dir}\n{str(e)}")

    def log_error(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("compression_errors.log", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n\n")

    def cancel(self):
        self.abort_flag = True
        self.progress["value"] = 0
        self.btn_start["state"] = "normal"
        self.window.update()

if __name__ == "__main__":
    app = PictureCompressor()
    app.window.mainloop()
