"""Sarob logosi: sahro ufqidagi quyosh va sarob (havo titrashi) to'lqinlari."""
import math, os, sys
from PIL import Image, ImageDraw, ImageFilter

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
S = 1024  # katta o'lchamda chizib, keyin kichraytiramiz


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def draw_logo(bg_dark=True):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    # Fon: chuqur tungi-ko'k doira, pastga qarab binafsharang
    bg = Image.new("RGBA", (S, S))
    bd = ImageDraw.Draw(bg)
    top, bot = (24, 22, 58), (66, 30, 74)
    for y in range(S):
        bd.line([(0, y), (S, y)], fill=lerp(top, bot, y / S) + (255,))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, S - 1, S - 1], fill=255)
    img.paste(bg, (0, 0), mask)

    # Quyosh: oltin-to'q sariq gradient, ufqdan yarim chiqqan
    sun = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    cx, cy, r = S // 2, int(S * 0.56), int(S * 0.27)
    for y in range(cy - r, cy + 1):
        t = (y - (cy - r)) / r
        col = lerp((255, 214, 102), (255, 112, 67), t) + (255,)
        dx = int(math.sqrt(max(r * r - (y - cy) ** 2, 0)))
        sd.line([(cx - dx, y), (cx + dx, y)], fill=col)
    # Quyosh atrofida yumshoq nur
    glow = sun.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, Image.composite(glow, Image.new("RGBA", (S, S)), mask))
    img = Image.alpha_composite(img, Image.composite(sun, Image.new("RGBA", (S, S)), mask))

    # Sarob to'lqinlari: ufq ostida titrayotgan chiziqlar (aks)
    d = ImageDraw.Draw(img)
    waves = [(0.62, 0.62, 30), (0.70, 0.50, 26), (0.78, 0.36, 22), (0.86, 0.22, 18)]
    for i, (yy, width, thick) in enumerate(waves):
        y0 = S * yy
        half = S * width / 2
        col = lerp((255, 196, 92), (255, 120, 90), i / 3) + (int(255 * (1 - i * 0.18)),)
        # Silliq chiziq: zich joylashgan doirachalarni bir qatlamga chizamiz
        layer = Image.new("L", (S, S), 0)
        ld = ImageDraw.Draw(layer)
        n = 1500
        for k in range(n + 1):
            x = cx - half + (2 * half) * k / n
            y = y0 + math.sin(k / n * math.pi * 4 + i) * S * 0.012
            ld.ellipse([x - thick / 2, y - thick / 2, x + thick / 2, y + thick / 2], fill=col[3])
        img.paste(Image.new("RGBA", (S, S), col[:3] + (255,)), (0, 0), layer)

    # Doira chetidan tashqarisini kesib tashlash
    final = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    final.paste(img, (0, 0), mask)
    return final


logo = draw_logo()


def save(name, size, square_bg=None):
    im = logo.resize((size, size), Image.LANCZOS)
    if square_bg:
        base = Image.new("RGBA", (size, size), square_bg)
        base.alpha_composite(im)
        im = base
    im.save(os.path.join(OUT, name))


for name, size in [("favicon.png", 512), ("logo.png", 512), ("favicon-dark.png", 512),
                   ("favicon-96x96.png", 96), ("web-app-manifest-192x192.png", 192),
                   ("web-app-manifest-512x512.png", 512)]:
    save(name, size)
save("apple-touch-icon.png", 180, square_bg=(24, 22, 58, 255))
logo.resize((256, 256), Image.LANCZOS).save(os.path.join(OUT, "favicon.ico"),
                                             sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

# Splash: oq va qora fon uchun markazdagi logo
for name, bg in [("splash.png", (255, 255, 255, 0)), ("splash-dark.png", (0, 0, 0, 0))]:
    im = Image.new("RGBA", (512, 512), bg)
    im.alpha_composite(logo.resize((512, 512), Image.LANCZOS))
    im.save(os.path.join(OUT, name))

# favicon.svg o'rniga PNG ichiga o'ralgan SVG
import base64, io
buf = io.BytesIO(); logo.resize((256, 256), Image.LANCZOS).save(buf, "PNG")
svg = ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 256 256">'
       f'<image width="256" height="256" xlink:href="data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"/></svg>')
open(os.path.join(OUT, "favicon.svg"), "w").write(svg)
print("logo tayyor:", sorted(os.listdir(OUT)))
