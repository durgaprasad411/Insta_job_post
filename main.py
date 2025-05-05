from PIL import Image, ImageDraw, ImageFont
import tkinter as tk
from tkinter import simpledialog, messagebox
import os

# Constants
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1350  # Instagram portrait size
BACKGROUND_COLOR = (255, 255, 255)  # White
PRIMARY_COLOR = (30, 50, 90)  # Dark blue
FIELD_COLOR = (70, 70, 70)  # Dark gray for fields
VALUE_COLOR = (41, 128, 185)  # Blue for values
ACCENT_COLOR = (230, 80, 70)  # Red for important elements
BORDER_COLOR = (200, 200, 200)  # Light gray for borders
FONT_PATH = "arialbd.ttf"  # Bold font for better readability
HEADER_FONT_SIZE = 72
FIELD_FONT_SIZE = 48
VALUE_FONT_SIZE = 52
APPLY_FONT_SIZE = 36  # Reduced for better URL fitting
URL_FONT_SIZE = 28    # Special smaller size for URLs
MARGIN_X = 80
MARGIN_Y = 80
LINE_SPACING = 20
FIELD_PADDING = 40
SECTION_SPACING = 60  # Space between header and first field
BORDER_WIDTH = 4
MIN_APPLY_BOX_HEIGHT = 120  # Increased slightly
HEADER_LINE_SPACING = 40  # Extra space between header and line
MAX_URL_WIDTH = IMAGE_WIDTH - 2 * MARGIN_X - 40  # Max width for URL before breaking

def get_text_dimensions(text, font):
    """Get precise text dimensions using textbbox."""
    temp_image = Image.new('RGB', (1, 1))
    temp_draw = ImageDraw.Draw(temp_image)
    bbox = temp_draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def draw_bordered_rectangle(draw, coordinates, radius=0, width=BORDER_WIDTH):
    """Draw a rectangle with border lines."""
    x1, y1, x2, y2 = coordinates
    # Outer border
    draw.rectangle([x1, y1, x2, y2], outline=BORDER_COLOR, width=width)
    # Inner border (smaller)
    draw.rectangle(
        [x1+width, y1+width, x2-width, y2-width], 
        outline=BORDER_COLOR, 
        width=width
    )

def create_job_posting_image(data, output_path="job_posting.png"):
    """Create a job post with dynamic apply box sizing and proper spacing."""
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)
    
    try:
        header_font = ImageFont.truetype(FONT_PATH, HEADER_FONT_SIZE)
        field_font = ImageFont.truetype(FONT_PATH, FIELD_FONT_SIZE)
        value_font = ImageFont.truetype(FONT_PATH, VALUE_FONT_SIZE)
        apply_font = ImageFont.truetype(FONT_PATH, APPLY_FONT_SIZE)
        url_font = ImageFont.truetype(FONT_PATH, URL_FONT_SIZE)
        footer_font = ImageFont.truetype(FONT_PATH, 32)
    except:
        header_font = ImageFont.load_default()
        field_font = ImageFont.load_default()
        value_font = ImageFont.load_default()
        apply_font = ImageFont.load_default()
        url_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()
    
    # --- MAIN BORDER ---
    draw_bordered_rectangle(draw, [20, 20, IMAGE_WIDTH-20, IMAGE_HEIGHT-20], width=6)
    
    # --- HEADER SECTION ---
    header = "JOB OPPORTUNITY"
    header_width, header_height = get_text_dimensions(header, header_font)
    draw.text(
        ((IMAGE_WIDTH - header_width) // 2, MARGIN_Y),
        header,
        fill=PRIMARY_COLOR,
        font=header_font
    )
    
    # Header underline with extra space
    line_y = MARGIN_Y + header_height + HEADER_LINE_SPACING
    draw.line([(MARGIN_X, line_y), (IMAGE_WIDTH - MARGIN_X, line_y)], 
              fill=BORDER_COLOR, width=3)
    
    # --- JOB DETAILS SECTION ---
    y_position = line_y + SECTION_SPACING
    
    # Calculate maximum field label width for alignment
    field_labels = [f"{field}:" for field in data.keys() if field != "Apply Link"]
    max_label_width = max(get_text_dimensions(label, field_font)[0] for label in field_labels)
    
    # Field display order
    display_order = [
        "Company Name",
        "Qualification",
        "Years of Experience",
        "Salary",
        "Location"
    ]
    
    # Draw each field with borders
    for field in display_order:
        if field not in data:
            continue
            
        # Field label
        label = f"{field}:"
        draw.text(
            (MARGIN_X + 20, y_position),
            label,
            fill=FIELD_COLOR,
            font=field_font
        )
        
        # Field value
        value = data[field]
        value_x = MARGIN_X + max_label_width + 50
        
        # Split long values into multiple lines
        max_value_width = IMAGE_WIDTH - value_x - MARGIN_X - 40
        value_lines = split_text(value, value_font, max_value_width)
        
        # Draw each line of the value
        for i, line in enumerate(value_lines):
            draw.text(
                (value_x, y_position + (i * (VALUE_FONT_SIZE + LINE_SPACING))),
                line,
                fill=VALUE_COLOR,
                font=value_font
            )
        
        # Calculate total height for this field
        field_height = max(
            get_text_dimensions(label, field_font)[1],
            len(value_lines) * (VALUE_FONT_SIZE + LINE_SPACING)
        )
        
        # Draw horizontal line separator
        if field != display_order[-1]:
            separator_y = y_position + field_height + FIELD_PADDING//2
            draw.line([(MARGIN_X, separator_y), (IMAGE_WIDTH - MARGIN_X, separator_y)], 
                      fill=BORDER_COLOR, width=2)
            y_position = separator_y + FIELD_PADDING//2
        else:
            y_position += field_height + FIELD_PADDING
    
    # --- IMPROVED APPLY BUTTON WITH URL HANDLING ---
    apply_text = "APPLY NOW:"
    url_text = data['Apply Link']
    
    # Calculate required box height
    apply_font = url_font  # Use smaller font for URL
    url_lines = split_text(url_text, url_font, IMAGE_WIDTH - 2*MARGIN_X - 80)
    
    apply_box_height = max(
        MIN_APPLY_BOX_HEIGHT,
        (len(url_lines) * (URL_FONT_SIZE + 10) + 60)  # Extra space for "APPLY NOW"
    )
    
    # Position the apply box
    apply_y = IMAGE_HEIGHT - apply_box_height - 80
    apply_rect_width = IMAGE_WIDTH - 2*MARGIN_X
    
    # Outer border
    draw_bordered_rectangle(
        draw, 
        [MARGIN_X, apply_y, IMAGE_WIDTH-MARGIN_X, apply_y+apply_box_height],
        width=4
    )
    
    # Inner filled rectangle
    draw.rectangle(
        [MARGIN_X+8, apply_y+8, IMAGE_WIDTH-MARGIN_X-8, apply_y+apply_box_height-8],
        fill=ACCENT_COLOR,
        outline=ACCENT_COLOR
    )
    
    # Draw "APPLY NOW" text
    apply_now_width, apply_now_height = get_text_dimensions(apply_text, apply_font)
    draw.text(
        ((IMAGE_WIDTH - apply_now_width) // 2, 
         apply_y + 20),
        apply_text,
        fill=BACKGROUND_COLOR,
        font=apply_font
    )
    
    # Draw URL lines (centered)
    for i, line in enumerate(url_lines):
        line_width, line_height = get_text_dimensions(line, url_font)
        draw.text(
            ((IMAGE_WIDTH - line_width) // 2, 
             apply_y + 50 + (i * (URL_FONT_SIZE + 5))),
            line,
            fill=BACKGROUND_COLOR,
            font=url_font
        )
    
    # --- FOOTER ---
    footer_y = IMAGE_HEIGHT - 50
    company_name = data["Company Name"].upper()
    footer_text = f"© {company_name} CAREERS"
    footer_width, _ = get_text_dimensions(footer_text, footer_font)
    draw.text(
        ((IMAGE_WIDTH - footer_width) // 2, footer_y),
        footer_text,
        fill=FIELD_COLOR,
        font=footer_font
    )
    
    # Save image
    image.save(output_path)
    return output_path

def split_text(text, font, max_width):
    """Improved text splitting that handles URLs better."""
    # Special handling for URLs
    if text.startswith(('http://', 'https://')):
        parts = []
        while len(text) > 0:
            # Find the last slash that keeps us under max width
            split_pos = len(text)
            while split_pos > 0:
                test_text = text[:split_pos]
                test_width, _ = get_text_dimensions(test_text, font)
                if test_width <= max_width:
                    parts.append(test_text)
                    text = text[split_pos:]
                    break
                else:
                    # Look for the previous slash to break at
                    new_split_pos = text.rfind('/', 0, split_pos-1)
                    split_pos = new_split_pos if new_split_pos > 0 else split_pos-1
        return parts
    
    # Normal text splitting
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

def collect_job_data():
    """Collect job data through a simple GUI."""
    root = tk.Tk()
    root.withdraw()
    
    fields = {
        "Company Name": "Enter company name (e.g., Google):",
        "Qualification": "Required qualification (e.g., B.Tech CS):",
        "Years of Experience": "Experience needed (e.g., 3-5 years):",
        "Salary": "Salary/package (e.g., ₹10-12 LPA):",
        "Location": "Job location (e.g., Bangalore):",
        "Apply Link": "Application URL or email:"
    }
    
    data = {}
    
    for field, prompt in fields.items():
        while True:
            value = simpledialog.askstring(field, prompt)
            if value:
                data[field] = value
                break
            else:
                messagebox.showerror("Error", f"{field} is required!")
    
    return data

def main():
    print("Professional Job Post Generator with Dynamic Apply Box")
    job_data = collect_job_data()
    
    output_filename = f"{job_data['Company Name'].replace(' ', '_')}_job_post.png"
    try:
        image_path = create_job_posting_image(job_data, output_filename)
        messagebox.showinfo("Success", 
              f"Job post created with dynamic apply box!\nSaved as: {os.path.abspath(image_path)}")
        print(f"Image saved: {os.path.abspath(image_path)}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create image: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()