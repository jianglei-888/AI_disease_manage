"""
最简 81x81 PNG tabBar 图标生成（手绘像素法）。
颜色：未选中 #6E6A62  /  选中 #E8A87C  /  背景透明
不依赖任何第三方库（只用 zlib / struct）。
"""
import os
import zlib
import struct

SIZE = 81
DARK = (110, 106, 98, 255)      # 未选中
WARM = (232, 168, 124, 255)     # 选中
ACCENT = (224, 122, 95, 255)    # 红点
TRANSPARENT = (0, 0, 0, 0)

# === 工具：将 RGBA 列表写成 PNG ===
def make_png(pixels, w, h):
    def chunk(tag, data):
        return (struct.pack('>I', len(data)) + tag + data
                + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff))
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)  # 8bit RGBA
    raw = b''
    for y in range(h):
        raw += b'\x00'  # filter
        for x in range(w):
            r, g, b, a = pixels[y * w + x]
            raw += struct.pack('BBBB', r, g, b, a)
    idat = zlib.compress(raw, 9)
    return sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')


def blank_pixels():
    return [TRANSPARENT] * (SIZE * SIZE)


def set_px(pix, x, y, color):
    if 0 <= x < SIZE and 0 <= y < SIZE:
        pix[y * SIZE + x] = color


def fill_rect(pix, x0, y0, x1, y1, color):
    for y in range(max(0, y0), min(SIZE, y1 + 1)):
        for x in range(max(0, x0), min(SIZE, x1 + 1)):
            set_px(pix, x, y, color)


def fill_circle(pix, cx, cy, r, color):
    for y in range(max(0, cy - r), min(SIZE, cy + r + 1)):
        for x in range(max(0, cx - r), min(SIZE, cx + r + 1)):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                set_px(pix, x, y, color)


def stroke_rect(pix, x0, y0, x1, y1, w, color):
    fill_rect(pix, x0, y0, x1, y0 + w - 1, color)
    fill_rect(pix, x0, y1 - w + 1, x1, y1, color)
    fill_rect(pix, x0, y0, x0 + w - 1, y1, color)
    fill_rect(pix, x1 - w + 1, y0, x1, y1, color)


def stroke_line(pix, x0, y0, x1, y1, w, color):
    # 简单 bresenham
    dx = abs(x1 - x0); sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0); sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        fill_rect(pix, x0 - w // 2, y0 - w // 2, x0 + w // 2, y0 + w // 2, color)
        if x0 == x1 and y0 == y1: break
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy


def stroke_circle(pix, cx, cy, r, w, color):
    # 描边圆环（用半径差近似）
    for y in range(max(0, cy - r - 1), min(SIZE, cy + r + 2)):
        for x in range(max(0, cx - r - 1), min(SIZE, cx + r + 2)):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if (r - w) ** 2 <= d2 <= r * r:
                set_px(pix, x, y, color)


# === 各图标 ===
def icon_home(color, accent=False):
    pix = blank_pixels()
    # 外框
    stroke_rect(pix, 12, 18, 68, 64, 3, color)
    # 顶部分隔
    stroke_line(pix, 12, 30, 68, 30, 3, color)
    # 内部两行
    stroke_line(pix, 22, 42, 38, 42, 3, color)
    stroke_line(pix, 22, 52, 50, 52, 3, color)
    if accent:
        # 右上红点
        fill_circle(pix, 60, 22, 5, ACCENT)
    return make_png(pix, SIZE, SIZE)


def icon_submit(color, accent=False):
    pix = blank_pixels()
    # 卡片外框
    stroke_rect(pix, 16, 12, 64, 70, 3, color)
    # 顶部分隔
    stroke_line(pix, 16, 24, 64, 24, 3, color)
    # 两个圆点（笔记本打孔）
    fill_circle(pix, 22, 18, 2, color)
    fill_circle(pix, 58, 18, 2, color)
    # 中间加号
    stroke_line(pix, 40, 36, 40, 56, 3, color)
    stroke_line(pix, 30, 46, 50, 46, 3, color)
    return make_png(pix, SIZE, SIZE)


def icon_chat(color, accent=False):
    pix = blank_pixels()
    # 对话框
    stroke_rect(pix, 10, 16, 70, 52, 3, color)
    # 左下小三角（嘴）
    fill_rect(pix, 18, 52, 22, 58, color)
    fill_rect(pix, 18, 58, 24, 60, color)
    # 三个点
    fill_circle(pix, 26, 36, 3, color)
    fill_circle(pix, 40, 36, 3, color)
    fill_circle(pix, 54, 36, 3, color)
    if accent:
        # 选中态：右上小红点提示
        fill_circle(pix, 64, 18, 5, ACCENT)
    return make_png(pix, SIZE, SIZE)


def icon_profile(color, accent=False):
    pix = blank_pixels()
    # 头
    stroke_circle(pix, 40, 28, 11, 3, color)
    # 肩
    stroke_line(pix, 14, 64, 14, 56, 3, color)
    stroke_line(pix, 14, 56, 22, 48, 3, color)
    stroke_line(pix, 22, 48, 58, 48, 3, color)
    stroke_line(pix, 58, 48, 66, 56, 3, color)
    stroke_line(pix, 66, 56, 66, 64, 3, color)
    if accent:
        fill_circle(pix, 40, 28, 4, ACCENT)
    return make_png(pix, SIZE, SIZE)


OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'images')
OUT_DIR = os.path.abspath(OUT_DIR)

ICONS = {
    'home.png':            icon_home,
    'home-active.png':     lambda c, a=False: icon_home(c, accent=True),
    'submit.png':          icon_submit,
    'submit-active.png':   lambda c, a=False: icon_submit(c, accent=True),
    'chat.png':            icon_chat,
    'chat-active.png':     lambda c, a=False: icon_chat(c, accent=True),
    'profile.png':         icon_profile,
    'profile-active.png':  lambda c, a=False: icon_profile(c, accent=True),
}

for fname, fn in ICONS.items():
    color = WARM if 'active' in fname else DARK
    data = fn(color)
    with open(os.path.join(OUT_DIR, fname), 'wb') as f:
        f.write(data)
    print('wrote', fname, len(data), 'bytes')
