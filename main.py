from PIL import Image, ImageDraw, ImageFont
import os
import streamlit as st  # Optional for web app error display

# === Constants ===
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1350
BACKGROUND_COLOR = (255, 255, 255)
PRIMARY_COLOR = (30, 50, 90)        # Header
FIELD_COLOR = (50, 50, 50)          # Field label
VALUE_COLOR = (0, 102, 204)         # Field value
ACCENT_COLOR = (220, 53, 69)        # Apply Now box
BORDER_COLOR = (180, 180, 180)

# === Fonts ===
FONT_PATH = "arialbd.ttf"  # or try 'DejaVuSans-Bold.ttf' if Arial not available
HEADER_FONT_SIZE = 80
FIELD_FONT_SIZE = 48
VALUE_FONT_SIZE = 52
APPLY_FONT_SIZE = 42
URL_FONT_SIZE = 30
FOOTER_FONT_SIZE = 32

# === Layout Settings ===
MARGIN_X = 80
MARGIN_Y = 100
FIELD_PADDING = 50
LINE_SPACING = 15
SECTION_SPACING = 60
MIN_APPLY_BOX_HEIGHT = 120
BORDER_WIDTH = 4

def get_text_dimensions(text, font):
    """Calculate text width and height using textbbox."""
    dummy_img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def split_text(text, font, max_width):
    """Split long text into lines based on width."""
    if text.startswith(('http://', 'https://')):
        parts = []
        while len(text) > 0:
            split_pos = len(text)
            while split_pos > 0:
                test_text = text[:split_pos]
                test_width, _ = get_text_dimensions(test_text, font)
                if test_width <= max_width:
                    parts.append(test_text)
                    text = text[split_pos:]
                    break
                else:
                    split_pos = text.rfind('/', 0, split_pos - 1)
                    if split_pos <= 0:
                        split_pos = len(text) - 1
        return parts

    words = text.split()
    lines, current_line = [], []
    for word in words:
        test_line = ' '.join(current_line + [word])
        width, _ = get_text_dimensions(test_line, font)
        if width <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    return lines

def draw_bordered_rectangle(draw, coords, width=BORDER_WIDTH):
    """Draw outer and inner borders."""
    x1, y1, x2, y2 = coords
    draw.rectangle([x1, y1, x2, y2], outline=BORDER_COLOR, width=width)

def create_job_posting_image(data, output_path="job_posting.png"):
    try:
        # === Image and Drawing Context ===
        image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(image)

        # === Font Loading ===
        def load_font(size):
            try:
                return ImageFont.truetype(FONT_PATH, size)
            except:
                return ImageFont.load_default()

        header_font = load_font(HEADER_FONT_SIZE)
        field_font = load_font(FIELD_FONT_SIZE)
        value_font = load_font(VALUE_FONT_SIZE)
        apply_font = load_font(APPLY_FONT_SIZE)
        url_font = load_font(URL_FONT_SIZE)
        footer_font = load_font(FOOTER_FONT_SIZE)

        # === Header ===
        header_text = "JOB OPPORTUNITY"
        header_width, header_height = get_text_dimensions(header_text, header_font)
        draw.text(
            ((IMAGE_WIDTH - header_width) // 2, MARGIN_Y),
            header_text,
            fill=PRIMARY_COLOR,
            font=header_font
        )

        # Header underline
        line_y = MARGIN_Y + header_height + 20
        draw.line([(MARGIN_X, line_y), (IMAGE_WIDTH - MARGIN_X, line_y)],
                  fill=BORDER_COLOR, width=3)

        y_position = line_y + SECTION_SPACING

        # === Fields ===
        display_fields = ["Company Name", "Qualification", "Years of Experience", "Salary", "Location"]
        max_label_width = max(get_text_dimensions(f"{field}:", field_font)[0] for field in display_fields)

        for field in display_fields:
            if field not in data:
                continue

            label = f"{field}:"
            value = data[field]

            draw.text((MARGIN_X, y_position), label, fill=FIELD_COLOR, font=field_font)

            value_x = MARGIN_X + max_label_width + 40
            value_width_limit = IMAGE_WIDTH - value_x - MARGIN_X
            value_lines = split_text(value, value_font, value_width_limit)

            for i, line in enumerate(value_lines):
                draw.text((value_x, y_position + i * (VALUE_FONT_SIZE + LINE_SPACING)), line, fill=VALUE_COLOR, font=value_font)

            field_height = max(
                get_text_dimensions(label, field_font)[1],
                len(value_lines) * (VALUE_FONT_SIZE + LINE_SPACING)
            )
            y_position += field_height + FIELD_PADDING

        # === APPLY NOW Section ===
        apply_label = "APPLY NOW:"
        url_text = data.get("Apply Link", "")
        url_lines = split_text(url_text, url_font, IMAGE_WIDTH - 2 * MARGIN_X - 80)

        apply_box_height = max(MIN_APPLY_BOX_HEIGHT, len(url_lines) * (URL_FONT_SIZE + 10) + 70)
        apply_y = IMAGE_HEIGHT - apply_box_height - 100

        draw_bordered_rectangle(draw, [MARGIN_X, apply_y, IMAGE_WIDTH - MARGIN_X, apply_y + apply_box_height])

        # Inner red box
        draw.rectangle([MARGIN_X + 6, apply_y + 6, IMAGE_WIDTH - MARGIN_X - 6, apply_y + apply_box_height - 6],
                       fill=ACCENT_COLOR)

        # Apply label
        label_width, _ = get_text_dimensions(apply_label, apply_font)
        draw.text(((IMAGE_WIDTH - label_width) // 2, apply_y + 20), apply_label, fill=BACKGROUND_COLOR, font=apply_font)

        # URL lines
        for i, line in enumerate(url_lines):
            line_width, _ = get_text_dimensions(line, url_font)
            draw.text(((IMAGE_WIDTH - line_width) // 2, apply_y + 60 + i * (URL_FONT_SIZE + 5)), line,
                      fill=BACKGROUND_COLOR, font=url_font)

        # === Footer ===
        company_footer = data["Company Name"].upper()
        footer_text = f"© {company_footer} CAREERS"
        footer_width, _ = get_text_dimensions(footer_text, footer_font)
        draw.text(((IMAGE_WIDTH - footer_width) // 2, IMAGE_HEIGHT - 50),
                  footer_text, fill=FIELD_COLOR, font=footer_font)

        # Save image
        image.save(output_path)
        return output_path

    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None
