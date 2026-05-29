from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
from datetime import datetime
import discord
import aiohttp
import os
from io import BytesIO

# ======================
# FOLDER
# ======================
ASSETS_FOLDER = "assets"

# ======================
# FONT
# ======================
FONT_BOLD = os.path.join( ASSETS_FOLDER, "BJCree-Bold.ttf")
USER_FONT = ImageFont.truetype(FONT_BOLD, 24)
TEXT_FONT = ImageFont.truetype(FONT_BOLD, 24)
JOIN_FONT = ImageFont.truetype(FONT_BOLD, 18)

# ======================
# BACKGROUND CACHE
# ======================
BACKGROUND_CACHE = {}

# ======================
# BULAN CACHE
# ======================
BULAN = { 1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"}

# ======================
# TEXT CENTER POINT
# ======================
USERNAME_CENTER_X = 325
GAME_CENTER_X = 325
DATE_CENTER_X = 810

# ======================
# TEXT POSITION Y
# ======================
USERNAME_Y = 162
GAME_Y = 248

# ======================
# DOWNLOAD AVATAR
# ======================
async def get_avatar(url):

    async with aiohttp.ClientSession() as session:

        async with session.get(url) as resp:

            data = await resp.read()
            return Image.open(
                BytesIO(data)
            ).convert("RGBA")

# ======================
# ROUNDED AVATAR
# ======================
def rounded_avatar(
    img,
    size=(180, 179),
    radius=8
):

    img = img.resize(size, Image.LANCZOS)

    mask = Image.new("L", size, 0)

    draw = ImageDraw.Draw(mask)

    draw.rounded_rectangle(
        (0, 0, size[0], size[1]),
        radius=radius,
        fill=255
    )

    output = ImageOps.fit(
        img,
        mask.size,
        centering=(0.5, 0.5)
    )

    output.putalpha(mask)

    return output

# ======================
# GET CENTER X
# ======================
def get_text_center_x(
    draw,
    text,
    font,
    center_x
):

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    text_width = bbox[2] - bbox[0]

    return int(
        center_x - (text_width / 2)
    )

# ======================
# GLOW TEXT
# ======================
def draw_glow_text(
    base,
    position,
    text,
    font,
    text_color=(255, 255, 255),
    glow_color=(255, 140, 0),
    glow_radius=18
):

    x, y = position

    # glow
    glow_layer = Image.new(
        "RGBA",
        base.size,
        (0, 0, 0, 0)
    )

    glow_draw = ImageDraw.Draw(glow_layer)

    glow_draw.text(
        (x, y),
        text,
        font=font,
        fill=glow_color
    )

    glow_layer = glow_layer.filter(
        ImageFilter.GaussianBlur(glow_radius)
    )

    base.alpha_composite(glow_layer)

    # main text
    final_draw = ImageDraw.Draw(base)

    final_draw.text(
        (x, y),
        text,
        font=font,
        fill=text_color,
        stroke_width=2,
        stroke_fill=(0, 0, 0)
    )

# ======================
# GENERATE CARD
# ======================
async def generate_card(
    avatar,
    user: discord.User,
    game_text: str,
    background_name: str,
    glow_color=(255, 140, 0),
    display_name=None,
    joined_at=None
):

    # ======================
    # LOAD BACKGROUND
    # ======================
    if background_name not in BACKGROUND_CACHE:
        bg_path = os.path.join(
            ASSETS_FOLDER,
            background_name
        )
        bg = Image.open(bg_path).convert("RGBA")
        bg = bg.resize((1000, 350))
        BACKGROUND_CACHE[background_name] = bg
        
    background = BACKGROUND_CACHE[
        background_name
    ].copy()

    avatar = rounded_avatar(avatar)
    background.paste(
        avatar,
        (717, 45),
        avatar
    )

    # ======================
    # DRAW
    # ======================
    draw = ImageDraw.Draw(background)

    # ======================
    # USERNAME
    # ======================
    username_text = (
        display_name or user.name
    )

    username_x = get_text_center_x(
        draw,
        username_text,
        USER_FONT,
        USERNAME_CENTER_X
    )

    draw_glow_text(
        background,
        (username_x, USERNAME_Y),
        username_text,
        USER_FONT
    )

    # ======================
    # GAME TEXT
    # ======================
    game_x = get_text_center_x(
        draw,
        game_text,
        TEXT_FONT,
        GAME_CENTER_X
    )

    draw.text(
        (game_x, GAME_Y),
        game_text,
        font=TEXT_FONT,
        fill=(220, 220, 220),
        stroke_width=2,
        stroke_fill=(0, 0, 0)
    )

    # ======================
    # JOIN DATE
    # ======================
    if joined_at:

        try:

            dt = datetime.fromisoformat(
                joined_at
            )

            formatted_date = (
                f"{dt.day} "
                f"{BULAN[dt.month]} "
                f"{dt.year}"
            )

        except Exception:

            formatted_date = joined_at

        join_x = get_text_center_x(
            draw,
            formatted_date,
            JOIN_FONT,
            DATE_CENTER_X
        )

        draw.text(
            (join_x, 260),
            formatted_date,
            font=JOIN_FONT,
            fill=(255, 255, 255),
            stroke_width=1,
            stroke_fill=(0, 0, 0)
        )

    # ======================
    # EXPORT BUFFER
    # ======================
    buffer = BytesIO()

    background.save(
        buffer,
        format="PNG"
    )

    buffer.seek(0)

    return buffer