from flask import Flask, request, send_file, render_template
from PIL import Image, ImageDraw, ImageFont
import io, os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    name = request.form['name']
    photo = request.files['photo']

    # Validate name: max 2 words and max 14 letters (excluding spaces)
    words = name.strip().split()
    if len(words) > 2:
        return "Please enter only 2 words maximum."
    if len(''.join(words)) > 14:
        return "Name too long. Please use 14 letters or less."

    # Convert name to Sentence Case (each word capitalized, rest lowercase)
    words = [w.lower().capitalize() for w in words]
    name = ' '.join(words)

    # Load template
    base = Image.open('static/template.png').convert('RGBA')
    base_width, base_height = base.size

    # ==== Photo Placement Config ====
    photo_x = 158
    photo_y = 324
    photo_width = 243
    photo_height = 249
    photo_shape = 'rounded'

    # Load uploaded image
    user_img = Image.open(photo).convert('RGBA')
    img_w, img_h = user_img.size

    # Resize image proportionally
    img_ratio = img_w / img_h
    box_ratio = photo_width / photo_height

    if img_ratio > box_ratio:
        new_width = photo_width
        new_height = int(photo_width / img_ratio)
    else:
        new_height = photo_height
        new_width = int(photo_height * img_ratio)

    user_img = user_img.resize((new_width, new_height), Image.LANCZOS)

    # Create mask
    mask = Image.new('L', (new_width, new_height), 0)
    draw_mask = ImageDraw.Draw(mask)
    if photo_shape == 'circle':
        draw_mask.ellipse((0, 0, new_width, new_height), fill=255)
    elif photo_shape == 'rounded':
        radius = int(min(new_width, new_height) * 0.2)
        draw_mask.rounded_rectangle((0, 0, new_width, new_height), radius=radius, fill=255)
    elif photo_shape == 'rectangle':
        draw_mask.rectangle((0, 0, new_width, new_height), fill=255)
    elif photo_shape == 'triangle':
        draw_mask.polygon([
            (new_width // 2, 0),
            (0, new_height),
            (new_width, new_height)
        ], fill=255)
    elif photo_shape == 'square':
        draw_mask.rectangle((0, 0, new_width, new_height), fill=255)

    user_img.putalpha(mask)

    # Paste cropped image centered
    offset_x = photo_x + (photo_width - new_width) // 2
    offset_y = photo_y + (photo_height - new_height) // 2
    base.paste(user_img, (offset_x, offset_y), user_img)

    # ==== Name Text Placement ====
    draw = ImageDraw.Draw(base)
    try:
        font_size = int(base_width * 0.045)
        font = ImageFont.truetype('fonts/Poppins-Medium.ttf', size=font_size)
    except:
        font = ImageFont.load_default()

    text_color = "#914f26"
    line_spacing = int(font_size * 1)

    text_area_x = 75
    text_area_y = 515
    text_area_width = 412
    text_area_height = 268

    total_text_height = len(words) * line_spacing
    start_y = text_area_y + (text_area_height - total_text_height) // 2

    for i, word in enumerate(words):
        text_width = draw.textlength(word, font=font)
        text_x = text_area_x + (text_area_width - text_width) // 2
        text_y = start_y + i * line_spacing
        draw.text((text_x, text_y), word, font=font, fill=text_color)

    # Save to /static/generated/
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    output_path = f'static/generated/poster_{timestamp}.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    base.save(output_path)

    return f"/{output_path}"

if __name__ == '__main__':
    app.run(debug=True)