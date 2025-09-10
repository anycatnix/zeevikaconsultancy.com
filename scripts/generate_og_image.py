from PIL import Image, ImageDraw, ImageFont
import os

def create_og_image():
    # Create a blank image with the recommended OG size (1200x630)
    width, height = 1200, 630
    background_color = (25, 55, 65)  # Dark teal
    text_color = (255, 255, 255)    # White
    
    # Create image
    image = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(image)
    
    # Add text
    try:
        # Try to use a nice font if available, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except IOError:
            font = ImageFont.load_default()
            
        text = "Zeevika Consultancy"
        text_width = draw.textlength(text, font=font)
        
        # Center the text
        x = (width - text_width) // 2
        y = (height - 60) // 2  # 60 is the font size
        
        draw.text((x, y), text, fill=text_color, font=font)
        
        # Save the image
        os.makedirs(os.path.join('static', 'images'), exist_ok=True)
        image_path = os.path.join('static', 'images', 'og-default.jpg')
        image.save(image_path, 'JPEG', quality=85)
        print(f"Created default OG image at: {os.path.abspath(image_path)}")
        
    except Exception as e:
        print(f"Error creating OG image: {e}")

if __name__ == "__main__":
    create_og_image()
