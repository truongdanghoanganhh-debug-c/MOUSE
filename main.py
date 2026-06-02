import mss
from PIL import Image
import ctypes
import time
import numpy as np
import keyboard
import colorama
import pystyle
import os
import shutil
import subprocess
from time import sleep
import sys
import math
from flask import Flask, render_template, request, redirect, url_for
import logging
import threading

# Import các hàm bổ trợ từ các file nội bộ trong thư mục consmath
from consmath.logitech import *
from consmath.crackcailonmemay import *  # Giữ nguyên import để tránh lỗi cấu trúc thư mục hiện tại

# Khởi tạo Flask App phục vụ Giao diện Web (Web Menu)
app = Flask(__name__)

# Cấu hình phím bấm và màu sắc hợp lệ
VALID_KEYS = ['x1', 'alt', 'ctrl', 'shift', 'chuot_trai', 'chuot_phai', 'x2', 'f1', 'f2', 'space']
VALID_COLORS = ['purple', 'yellow', 'red']

def read_config(file_path="config.txt"):
    config = {}
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if ":" in line:
                    key, value = line.strip().split(":", 1)
                    config[key.strip()] = value.strip()
    except FileNotFoundError:
        config = {
            "Phim kich hoat": "x1",
            "Do nhay mau": "120",
            "FOV quet ngang": "65",
            "FOV quet doc": "30",
            "Mau dich": "purple",
            "Do muot (Cang cao cang muot)": "12",
            "offset Y": "4",
            "offset X": "0"
        }
    return config

def write_config(config, file_path="config.txt"):
    with open(file_path, "w", encoding="utf-8") as file:
        for key, value in config.items():
            file.write(f"{key}: {value}\n")

@app.route('/')
def index():
    config = read_config()
    return render_template('index.html', config=config, valid_keys=VALID_KEYS, valid_colors=VALID_COLORS)

@app.route('/save', methods=['POST'])
def save_config():
    config = read_config()
    config["Phim kich hoat"] = request.form.get("Phim kich hoat", config["Phim kich hoat"])
    config["Do nhay mau"] = request.form.get("Do nhay mau", config["Do nhay mau"])
    config["FOV quet ngang"] = request.form.get("FOV quet ngang", config["FOV quet ngang"])
    config["FOV quet doc"] = request.form.get("FOV quet doc", config["FOV quet doc"])
    config["Mau dich"] = request.form.get("Mau dich", config["Mau dich"])
    config["Do muot (Cang cao cang muot)"] = request.form.get("Do muot (Cang cao cang muot)", config["Do muot (Cang cao cang muot)"])
    config["offset Y"] = request.form.get("offset Y", config["offset Y"])
    config["offset X"] = request.form.get("offset X", config["offset X"])

    try:
        do_nhay_mau = int(config["Do nhay mau"])
        if not (0 <= do_nhay_mau <= 255): return "Độ nhạy màu phải từ 0 đến 255", 400
        fov_ngang = int(config["FOV quet ngang"])
        fov_doc = int(config["FOV quet doc"])
        if fov_ngang <= 0 or fov_doc <= 0: return "FOV quét phải lớn hơn 0", 400
        do_muot = int(config["Do muot (Cang cao cang muot)"])
        if do_muot <= 0: return "Độ mượt phải lớn hơn 0", 400
        if config["Phim kich hoat"] not in VALID_KEYS: return "Phím kích hoạt không hợp lệ", 400
        if config["Mau dich"] not in VALID_COLORS: return "Màu đích không hợp lệ", 400
        offset_y = int(config["offset Y"])
        offset_x = int(config["offset X"])
    except ValueError:
        return "Giá trị số không hợp lệ", 400

    write_config(config)
    try:
        supanigaplusplusplusfrvuapproved()
        print_banner()
    except Exception:
        pass

    requested_with = request.headers.get('X-Requested-With', '')
    if requested_with.lower() in ("xmlhttprequest", "fetch"):
        return ("OK", 200)
    return redirect(url_for('index', saved=1))

def run_flask():
    try:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        log.disabled = True
        app.logger.disabled = True
        from flask import cli
        cli.show_server_banner = lambda *args: None
    except Exception:
        pass
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def check_admin_privileges():
    """Kiểm tra quyền Administrator của Script"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not check_admin_privileges():
    print("[hank666] Script cần chạy dưới quyền Administrator...")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit(0)

def load_hank666_kernel_driver():
    """Nạp driver hệ thống phục vụ giả lập chuột bypass"""
    driver_name = "hank666_driver"
    source_path = os.path.abspath(os.path.join("consmath", "svchost.sys"))
    target_path = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "System32", "drivers", "svchost.sys")

    if os.path.exists(target_path):
        print(f"[hank666] Driver đã tồn tại tại {target_path}, tiến hành nạp dịch vụ.")
    else:
        print(f"[hank666] Cài đặt driver hệ thống...")
        try:
            shutil.copy(source_path, target_path)
            print(f"[hank666] Đã copy thành phần hệ thống.")
        except PermissionError:
            print(f"[hank666] Lỗi: Không đủ thẩm quyền truy cập System32.")
            sys.exit(1)
        except Exception as e:
            print(f"[hank666] Lỗi sao chép: {e}")
            sys.exit(1)

    # Dọn dẹp dịch vụ cũ nếu trùng tên và đăng ký dịch vụ Kernel mới
    os.system(f'sc stop {driver_name} >nul 2>&1')
    os.system(f'sc delete {driver_name} >nul 2>&1')
    
    create_cmd = f'sc create {driver_name} type=kernel start=demand binPath="{target_path}"'
    os.system(create_cmd)
    
    start_cmd = f'sc start {driver_name}'
    os.system(start_cmd)

user32 = ctypes.windll.user32

def fancy_loader(title="Đang khởi tạo", duration=2.5, width=32):
    start = time.time()
    spinner = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
    spin_idx = 0
    while True:
        elapsed = time.time() - start
        progress = min(1.0, elapsed / max(0.001, duration))
        filled = int(width * progress)
        bar = "█" * filled + "░" * (width - filled)
        percent = int(progress * 100)
        line = f" {spinner[spin_idx]} {title} │{bar}│ {percent:3d}%"
        spin_idx = (spin_idx + 1) % len(spinner)
        print(pystyle.Colorate.Horizontal(pystyle.Colors.white_to_red, line, 1), end='\r', flush=True)
        if progress >= 1.0:
            break
        time.sleep(0.06)
    print(pystyle.Colorate.Horizontal(pystyle.Colors.white_to_red, f" ✓ {title} hoàn tất" + " " * (width // 2), 1))

def load_local_config(filename="config.txt"):
    config = {}
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            if ":" in line:
                key, value = line.strip().split(":", 1)
                config[key.strip()] = value.strip()
    return config

def get_config_int_value(config, key):
    value = config.get(key)
    if value is None or not value.isdigit():
        raise ValueError(f"[hank666] Giá trị cấu hình ({key}) không hợp lệ.")
    return int(value)

# Khởi tạo nạp cấu hình ban đầu
config = load_local_config()
offsetY = get_config_int_value(config, "offset Y")
offsetX = get_config_int_value(config, "offset X")
aimbot_status = True

# Các biến kích thước vùng quét lấy từ module bẻ khóa hoặc tính toán tọa độ
scan_area = (scan_area_x, scan_area_y) 

def click_mouse_event():
    """Mô phỏng sự kiện click chuột chuẩn Windows (Trường hợp không dùng driver)"""
    user32.mouse_event(0x0002 | 0x0004, 0, 0, 0, 0)

def get_target_color_rgb(color):
    """Xác định mã màu RGB mục tiêu dựa vào cấu hình trong game"""
    if color == "purple":
        return np.array([250, 100, 250])
    elif color == "yellow":
        return np.array([254, 254, 64])
    elif color == "red":
        return np.array([170, 5, 8])
    return np.array([250, 100, 250])

def apply_color_mask(frame, color):
    """Lọc độ lệch màu pixel so với màu gốc để phát hiện kẻ địch"""
    target_color = get_target_color_rgb(color)
    color_diff = np.abs(frame - target_color)
    color_distance = np.sum(color_diff, axis=2)
    return color_distance < color_threshold  # Biến 'color_threshold' kế thừa toàn cục

def get_screen_center():
    """Lấy tọa độ chính giữa màn hình Desktop hiện tại"""
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)
    return screen_width // 2, screen_height // 2

def capture_fov_screen(center_x, center_y, size):
    """Chụp siêu tốc vùng màn hình nhỏ xung quanh tâm ngắm (FOV) bằng mss"""
    width, height = size
    with mss.mss() as sct:
        bbox = (center_x - width // 2, center_y - height // 2, center_x + width // 2, center_y + height // 2)
        sct_img = sct.grab(bbox)
        return np.array(Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX'))

def calculate_aim_coordinates(screen, color):
    """Xử lý mảng ma trận pixel để tìm ra vị trí viền nhân vật gần tâm ngắm nhất"""
    mask = apply_color_mask(screen, color)
    points = np.transpose(np.nonzero(mask))
    if len(points) > 0:
        min_y = np.min(points[:, 0])
        highest_points = points[points[:, 0] == min_y]
        distances = np.abs(highest_points[:, 1] - scan_area_x // 2)
        best_point = highest_points[np.argmin(distances)]
        
        x_diff = best_point[1] - scan_area_x // 2
        y_diff = best_point[0] - scan_area_y // 2
        
        x_adjusted = x_diff + offsetX
        y_adjusted = y_diff + offsetY
        return int(x_adjusted), int(y_adjusted)
    return None, None

def execute_aimbot_loop():
    """Điều phối toàn bộ quá trình: Chụp -> Quét -> Điều khiển chuột"""
    center_x, center_y = get_screen_center()
    screen = capture_fov_screen(center_x, center_y, scan_area)
    if screen is None:
        return None, None
        
    current_color = config.get("Mau dich", "purple")
    target_x, target_y = calculate_aim_coordinates(screen, current_color)
    
    if target_x is not None and target_y is not None:
        # Gọi hàm mouse_move từ driver của thư mục logitech để di chuyển chuột phần cứng
        mouse_move(target_x, target_y)
        return target_x, target_y
    return None, None

if __name__ == "__main__":
    # 1. Nạp driver hệ thống
    load_hank666_kernel_driver()
    
    # 2. Hiệu ứng giao diện dòng lệnh
    fancy_loader("Đang tải driver & cấu hình", duration=2.8, width=36)
    print_banner()
    
    # 3. Khởi tạo kết nối driver Logitech chuột ngầm
    if not init():
        print("[hank666] Không thể liên kết driver chuột. Thoát...")
        sys.exit()
        
    # 4. Chạy Web Menu (Flask) ở một luồng (thread) song song
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    last_modified_time = os.path.getmtime("config.txt")
    
    # 5. Vòng lặp Core thời gian thực (Real-time Aimbot Loop)
    while True:
        # Tự động nạp lại cấu hình (Hot Reload) nếu file config.txt bị sửa đổi từ Web UI
        if os.path.getmtime("config.txt") > last_modified_time:
            config = load_local_config()
            offsetY = get_config_int_value(config, "offset Y")
            offsetX = get_config_int_value(config, "offset X")
            last_modified_time = os.path.getmtime("config.txt")
            print("[hank666] Cấu hình đã được cập nhật thành công!")
            
        # Kiểm tra xem phím kích hoạt (Ví dụ: Alt, Shift, X1...) có đang được giữ hay không
        if not is_key_pressed():
            time.sleep(0.001)
            continue
            
        # Thực thi dịch chuyển tâm ngắm về phía mục tiêu có màu chỉ định
        aimbot_x, aimbot_y = execute_aimbot_loop()
