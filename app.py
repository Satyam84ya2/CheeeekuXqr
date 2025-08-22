from flask import Flask, request, send_file, jsonify
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, SquareModuleDrawer, CircleModuleDrawer, GappedSquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask, RadialGradiantColorMask, SquareGradiantColorMask, HorizontalGradiantColorMask, VerticalGradiantColorMask
import io
from PIL import Image, ImageDraw
import math

app = Flask(__name__)

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

@app.route('/')
def home():
    return jsonify({
        "message": "UPI QR Code Generator API",
        "usage": {
            "without_amount": "/api/qr",
            "with_amount": "/api/qr?amount=100",
            "with_custom_name": "/api/qr?amount=100&name=YourName",
            "with_currency": "/api/qr?amount=100&currency=INR",
            "with_style": "/api/qr?amount=100&style=gradient&color1=FF5733&color2=FFBD33"
        },
        "styles": {
            "basic": "Default black and white",
            "rounded": "Rounded modules",
            "circles": "Circular modules", 
            "gradient": "Gradient colors (specify color1 and color2)",
            "gradient_vertical": "Vertical gradient",
            "gradient_radial": "Radial gradient"
        },
        "color_format": "Hex colors without # (e.g., FF5733 for orange)",
        "endpoints": {
            "api": "/api/qr",
            "health_check": "/health"
        },
        "upi_id": "satyam84ya@fam"
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "upi-qr-generator"})

@app.route('/api/qr')
def generate_qr():
    try:
        # Get parameters from query string
        amount = request.args.get('amount', '')
        name = request.args.get('name', 'Satyam')
        currency = request.args.get('currency', 'INR')
        style = request.args.get('style', 'basic')
        color1 = request.args.get('color1', '000000')  # Default black
        color2 = request.args.get('color2', 'FFFFFF')  # Default white
        
        # Validate amount if provided
        if amount and (not amount.replace('.', '').isdigit() or float(amount) < 0):
            return jsonify({"error": "Invalid amount provided"}), 400
        
        # Convert hex colors to RGB
        front_color = hex_to_rgb(color1)
        back_color = hex_to_rgb(color2)
        
        # UPI ID
        upi_id = "satyam84ya@fam"
        
        # Build UPI payment URL
        upi_url = f"upi://pay?pa={upi_id}&pn={name}&cu={currency}"
        if amount:
            upi_url += f"&am={amount}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=15,
            border=2,
        )
        qr.add_data(upi_url)
        qr.make(fit=True)
        
        # Choose style based on parameter
        if style == 'rounded':
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),
                color_mask=SolidFillColorMask(
                    front_color=front_color, 
                    back_color=back_color
                )
            )
        elif style == 'circles':
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=CircleModuleDrawer(),
                color_mask=SolidFillColorMask(
                    front_color=front_color, 
                    back_color=back_color
                )
            )
        elif style == 'gradient':
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=SquareModuleDrawer(),
                color_mask=HorizontalGradiantColorMask(
                    back_color=back_color,
                    center_color=front_color
                )
            )
        elif style == 'gradient_vertical':
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=SquareModuleDrawer(),
                color_mask=VerticalGradiantColorMask(
                    back_color=back_color,
                    center_color=front_color
                )
            )
        elif style == 'gradient_radial':
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=SquareModuleDrawer(),
                color_mask=RadialGradiantColorMask(
                    back_color=back_color,
                    center_color=front_color
                )
            )
        else:  # basic style
            img = qr.make_image(
                fill_color=front_color, 
                back_color=back_color
            )
        
        # Add a decorative border around the QR code
        img = add_decorative_border(img, style, front_color, back_color)
        
        # Save image to bytes buffer
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG', quality=95)
        img_buffer.seek(0)
        
        # Return the image
        return send_file(img_buffer, mimetype='image/png', 
                         as_attachment=False, 
                         download_name='upi_qr.png')
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def add_decorative_border(qr_img, style, front_color, back_color):
    # Create a larger canvas with a decorative border
    border_size = 40
    width, height = qr_img.size
    new_width = width + border_size * 2
    new_height = height + border_size * 2
    
    # Create a new image with background color
    base_img = Image.new('RGB', (new_width, new_height), color=back_color)
    draw = ImageDraw.Draw(base_img)
    
    # Draw different border styles based on QR style
    if style in ['gradient', 'gradient_vertical', 'gradient_radial']:
        # Gradient border
        for i in range(border_size):
            # Calculate gradient color
            ratio = i / border_size
            r = int(front_color[0] * (1 - ratio) + back_color[0] * ratio)
            g = int(front_color[1] * (1 - ratio) + back_color[1] * ratio)
            b = int(front_color[2] * (1 - ratio) + back_color[2] * ratio)
            
            draw.rectangle([i, i, new_width - i, new_height - i], outline=(r, g, b), width=1)
    
    elif style in ['rounded', 'circles']:
        # Decorative pattern border
        for i in range(0, border_size, 3):
            color = front_color if i % 6 == 0 else back_color
            draw.rectangle([i, i, new_width - i, new_height - i], outline=color, width=2)
    
    else:  # basic style
        # Simple solid border
        draw.rectangle([0, 0, new_width - 1, new_height - 1], outline=front_color, width=5)
        draw.rectangle([5, 5, new_width - 6, new_height - 6], outline=back_color, width=3)
        draw.rectangle([8, 8, new_width - 9, new_height - 9], outline=front_color, width=1)
    
    # Paste the QR code in the center
    qr_position = ((new_width - width) // 2, (new_height - height) // 2)
    base_img.paste(qr_img, qr_position)
    
    return base_img

# Handle CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(debug=True)
