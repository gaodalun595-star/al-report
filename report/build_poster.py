from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import textwrap

ROOT = Path('report')
ASSETS = ROOT / 'assets'
OUT = ASSETS / '專題海報.png'
W, H = 1400, 2100  # 2:3
BG = (248, 251, 255)
BLUE = (30, 80, 150)
DARK = (35, 45, 60)
MUTED = (90, 105, 125)
CARD = (255, 255, 255)
LINE = (210, 225, 242)
ACCENT = (0, 145, 180)

FONT_CANDIDATES = [
    r'C:\Windows\Fonts\msjh.ttc',
    r'C:\Windows\Fonts\msjhl.ttc',
    r'C:\Windows\Fonts\NotoSansCJK-Regular.ttc',
    r'C:\Windows\Fonts\mingliu.ttc',
]

def font(size, bold=False):
    candidates = [r'C:\Windows\Fonts\msjhbd.ttc'] + FONT_CANDIDATES if bold else FONT_CANDIDATES
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

F_TITLE = font(76, True)
F_SUB = font(28)
F_H = font(34, True)
F_BODY = font(25)
F_SMALL = font(21)
F_CAP = font(18)

img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)

# Header
margin = 70
d.rounded_rectangle([margin, 45, W-margin, 230], radius=34, fill=(226, 239, 255), outline=LINE, width=3)
d.text((margin+45, 75), '送貨 App 的進步', font=F_TITLE, fill=BLUE)
d.text((margin+50, 165), 'Agent Studio 專題展覽海報｜日期：2026-06-24', font=F_SUB, fill=MUTED)

# Helpers
def wrap_text(text, width):
    # CJK friendly approximate wrap: 1 CJK ~= 2 ascii units. Keep simple chunks.
    out = []
    for para in text.split('\n'):
        if not para:
            out.append('')
            continue
        line = ''
        units = 0
        for ch in para:
            u = 2 if ord(ch) > 127 else 1
            if units + u > width:
                out.append(line)
                line = ch
                units = u
            else:
                line += ch
                units += u
        if line:
            out.append(line)
    return out

def card(x, y, w, h, title, bullets, body_font=F_BODY):
    d.rounded_rectangle([x, y, x+w, y+h], radius=22, fill=CARD, outline=LINE, width=2)
    d.rectangle([x, y, x+w, y+58], fill=(238, 247, 255))
    d.text((x+24, y+14), title, font=F_H, fill=BLUE)
    yy = y + 78
    for b in bullets:
        prefix = '• '
        lines = wrap_text(b, max(28, int((w-70)/13)))
        if not lines:
            continue
        d.text((x+28, yy), prefix + lines[0], font=body_font, fill=DARK)
        yy += 34
        for line in lines[1:]:
            d.text((x+55, yy), line, font=body_font, fill=DARK)
            yy += 32
        yy += 6
    return yy

def fit_image(path, box, caption=None):
    x, y, w, h = box
    d.rounded_rectangle([x, y, x+w, y+h], radius=20, fill=CARD, outline=LINE, width=2)
    if not Path(path).exists():
        d.text((x+20, y+20), f'找不到圖片：{path}', font=F_SMALL, fill=(180, 0, 0))
        return
    im = Image.open(path).convert('RGB')
    cap_h = 34 if caption else 0
    im.thumbnail((w-28, h-28-cap_h), Image.LANCZOS)
    px = x + (w - im.width)//2
    py = y + 14 + (h-28-cap_h - im.height)//2
    img.paste(im, (px, py))
    if caption:
        tw = d.textlength(caption, font=F_CAP)
        d.text((x+(w-tw)/2, y+h-30), caption, font=F_CAP, fill=MUTED)

# Intro and interaction cards
card(margin, 270, 610, 345, '1 · 專題介紹', [
    '專題名稱：送貨 App 的進步',
    '一句話：可以拿來迅速填送貨進度',
    '主要使用者：想要寄貨的人',
    '想解決的問題：可以直接在這個 App 選擇想要的物流公司，並迅速寄貨',
], F_BODY)

card(margin+650, 270, 610, 345, '2 · 左欄與右欄互動', [
    '左欄自訂頁欄位：寄件人、收件人、地址、送貨包裹大小限制、銀行卡等',
    '左欄傳給 Agent：訂單、物流公司、銀行卡',
    'Agent 寫回：進度表',
    '例子：使用者拖曳圖標找到自家位置 → Agent 回傳經緯度',
], F_SMALL)

# Images
fit_image(ASSETS/'server-topology.png', (margin, 655, 610, 410), 'Server 環境：全班共用拓撲')
fit_image(ASSETS/'project-architecture.png', (margin+650, 655, 610, 410), '系統概覽：左欄自訂頁 ↔ 右欄 Agent')

#成果、創新、技術 cards
card(margin, 1105, 390, 330, '3 · 成果', [
    '選物流公司',
    '填資料（寄件人／收件人／地址）',
    '銀行卡付款',
    '選包裹大小',
], F_BODY)
card(margin+435, 1105, 390, 330, '4 · 創新／亮點', [
    '人們不用去各大物流公司一一對比，在這個 App 就能直接選想要的物流公司',
], F_BODY)
card(margin+870, 1105, 390, 330, '5 · 技術含量', [
    '地圖（map）的完善程度算不錯',
], F_BODY)

# Demo section
d.rounded_rectangle([margin, 1480, W-margin, 1995], radius=24, fill=CARD, outline=LINE, width=2)
d.rectangle([margin, 1480, W-margin, 1542], fill=(238, 247, 255))
d.text((margin+24, 1494), 'Demo 展示', font=F_H, fill=BLUE)
fit_image(ASSETS/'demo-01.png', (margin+40, 1570, W-2*margin-80, 390), '寄件頁 demo-01.png')

# Footer
d.text((margin, 2030), '海報文字依照專題報告內容製作；未包含 api_key 或 Router 位址。', font=F_SMALL, fill=MUTED)

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, 'PNG')
print(f'OK: {OUT} {OUT.stat().st_size} bytes')
