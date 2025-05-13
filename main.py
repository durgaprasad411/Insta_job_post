from PIL import Image, ImageDraw, ImageFont
import os

# Constants
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1350
BACKGROUND_COLOR = (255, 255, 255)
PRIMARY_COLOR = (30, 50, 90)
FIELD_COLOR = (70, 70, 70)
VALUE_COLOR = (41, 128, 185)
ACCENT_COLOR = (230, 80, 70)
BORDER_COLOR = (200, 200, 200)
FONT_PATH = "arialbd.ttf"
HEADER_FONT_SIZE = 72
FIELD_FONT_SIZE = 48
VALUE_FONT_SIZE = 52
APPLY_FONT_SIZE = 36
URL_FONT_SIZE = 28
MARGIN_X = 80
MARGIN_Y = 80
LINE_SPACING = 20
FIELD_PADDING = 40
SECTION_SPACING = 60
BORDER_WIDTH = 4
MIN_APPLY_BOX_HEIGHT = 120
HEADER_LINE_SPACING = 40
MAX_URL_WIDTH = IMAGE_WIDTH - 2 * MARGIN_X - 40

def get_text_dimensions(text, font):
    temp_image = Image.new('RGB', (1, 1))
    temp_draw = ImageDraw.Draw(temp_image)
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def split_text(text, font, max_width):
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
                    new_split_pos = text.rfind('/', 0, split_pos - 1)
                    split_pos = new_split_pos if new_split_pos > 0 else split_pos - 1
        return parts

    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        test_width, _ = get_text_dimensions(test_line, font)

        if test_width <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines

def draw_bordered_rectangle(draw, coordinates, radius=0, width=BORDER_WIDTH):
    x1, y1, x2, y2 = coordinates
    draw.rectangle([x1, y1, x2, y2], outline=BORDER_COLOR, width=width)
    draw.rectangle([x1 + width, y1 + width, x2 - width, y2 - width],
                   outline=BORDER_COLOR, width=width)

def create_job_posting_image(data, output_path="job_posting.png"):
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)

    try:
        # Load fonts
        try:
            header_font = ImageFont.truetype(FONT_PATH, HEADER_FONT_SIZE)
            field_font = ImageFont.truetype(FONT_PATH, FIELD_FONT_SIZE)
            value_font = ImageFont.truetype(FONT_PATH, VALUE_FONT_SIZE)
            apply_font = ImageFont.truetype(FONT_PATH, APPLY_FONT_SIZE)
            url_font = ImageFont.truetype(FONT_PATH, URL_FONT_SIZE)
            footer_font = ImageFont.truetype(FONT_PATH, 32)
        except:
            header_font = field_font = value_font = apply_font = url_font = footer_font = ImageFont.load_default()

        # Main border
        draw_bordered_rectangle(draw, [20, 20, IMAGE_WIDTH - 20, IMAGE_HEIGHT - 20], width=6)

        # Header
        header = "JOB OPPORTUNITY"
        header_width, header_height = get_text_dimensions(header, header_font)
        draw.text(((IMAGE_WIDTH - header_width) // 2, MARGIN_Y), header, fill=PRIMARY_COLOR, font=header_font)

        # Header underline
        line_y = MARGIN_Y + header_height + HEADER_LINE_SPACING
        draw.line([(MARGIN_X, line_y), (IMAGE_WIDTH - MARGIN_X, line_y)], fill=BORDER_COLOR, width=3)

        # Job Details
        y_position = line_y + SECTION_SPACING
        display_order = ["Company Name", "Qualification", "Years of Experience", "Salary", "Location"]

        # Label width
        field_labels = [f"{field}:" for field in display_order]
        max_label_width = max(get_text_dimensions(label, field_font)[0] for label in field_labels)

        for field in display_order:
            if field not in data:
                continue

            label = f"{field}:"
            draw.text((MARGIN_X + 20, y_position), label, fill=FIELD_COLOR, font=field_font)

            value = data[field]
            value_x = MARGIN_X + max_label_width + 50
            max_value_width = IMAGE_WIDTH - value_x - MARGIN_X - 40
            value_lines = split_text(value, value_font, max_value_width)

            for i, line in enumerate(value_lines):
                draw.text((value_x, y_position + (i * (VALUE_FONT_SIZE + LINE_SPACING))),
                          line, fill=VALUE_COLOR, font=value_font)

            field_height = max(
                get_text_dimensions(label, field_font)[1],
                len(value_lines) * (VALUE_FONT_SIZE + LINE_SPACING)
            )

            if field != display_order[-1]:
                separator_y = y_position + field_height + FIELD_PADDING // 2
                draw.line([(MARGIN_X, separator_y), (IMAGE_WIDTH - MARGIN_X, separator_y)],
                          fill=BORDER_COLOR, width=2)
                y_position = separator_y + FIELD_PADDING // 2
            else:
                y_position += field_height + FIELD_PADDING

        # Apply Now Box
        apply_text = "APPLY NOW:"
        url_text = data['Apply Link']
        url_lines = split_text(url_text, url_font, IMAGE_WIDTH - 2 * MARGIN_X - 80)
        apply_box_height = max(MIN_APPLY_BOX_HEIGHT, (len(url_lines) * (URL_FONT_SIZE + 10) + 60))

        apply_y = IMAGE_HEIGHT - apply_box_height - 80

        draw_bordered_rectangle(draw, [MARGIN_X, apply_y, IMAGE_WIDTH - MARGIN_X, apply_y + apply_box_height], width=4)

        draw.rectangle([MARGIN_X + 8, apply_y + 8, IMAGE_WIDTH - MARGIN_X - 8, apply_y + apply_box_height - 8],
                       fill=ACCENT_COLOR, outline=ACCENT_COLOR)

        apply_now_width, _ = get_text_dimensions(apply_text, apply_font)
        draw.text(((IMAGE_WIDTH - apply_now_width) // 2, apply_y + 20),
                  apply_text, fill=BACKGROUND_COLOR, font=apply_font)

        for i, line in enumerate(url_lines):
            line_width, _ = get_text_dimensions(line, url_font)
            draw.text(((IMAGE_WIDTH - line_width) // 2, apply_y + 50 + (i * (URL_FONT_SIZE + 5))),
                      line, fill=BACKGROUND_COLOR, font=url_font)

        # Footer
        footer_y = IMAGE_HEIGHT - 50
        company_name = data["Company Name"].upper()
        footer_text = f"© {company_name} CAREERS"
        footer_width, _ = get_text_dimensions(footer_text, footer_font)
        draw.text(((IMAGE_WIDTH - footer_width) // 2, footer_y), footer_text, fill=FIELD_COLOR, font=footer_font)

        # Save
        image.save(output_path)
        return output_path

    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None
