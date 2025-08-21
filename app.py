from flask import Flask, request, send_file, jsonify
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, SquareModuleDrawer, CircleModuleDrawer, GappedSquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask, RadialGradiantColorMask, SquareGradiantColorMask, HorizontalGradiantColorMask, VerticalGradiantColorMask
import io
from PIL import Image, ImageDraw, ImageFilter

app = Flask(__name__)

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
        
        # UPI ID
        upi_id = "satyam84ya@fam"
        
        # Build UPI payment URL
        upi_url = f"upi://pay?pa={upi_id}&pn={name}&cu={currency}"
        if amount:
            upi_url += f"&am={amount}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # Higher error correction for styled QR codes
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
                    front_color=f"#{color1}", 
                    back_color=f"#{color2}"
                )
            )
        elif style == 'circles':
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=CircleModuleDrawer(),
                color_mask=SolidFillColorMask(
                    front_color=f"#{color1}", 
                    back_color=f"#{color2}"
                )
            )
        elif style == 'gradient':
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=SquareModuleDrawer(),
                color_mask=HorizontalGradiantColorMask(
                    back_color=f"#{color2}",
                    top_color=f"#{color1}",
                    bottom_color=f"#{color2}"
                )
            )
        elif style == 'gradient_vertical':
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=SquareModuleDrawer(),
                color_mask=VerticalGradiantColorMask(
                    back_color=f"#{color2}",
                    left_color=f"#{color1}",
                    right_color=f"#{color2}"
                )
            )
        elif style == 'gradient_radial':
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=SquareModuleDrawer(),
                color_mask=RadialGradiantColorMask(
                    back_color=f"#{color2}",
                    center_color=f"#{color1}",
                    edge_color=f"#{color2}"
                )
            )
        else:  # basic style
            img = qr.make_image(
                fill_color=f"#{color1}", 
                back_color=f"#{color2}"
            )
        
        # Add a decorative border around the QR code
        img = add_decorative_border(img, style)
        
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

def add_decorative_border(qr_img, style):
    # Create a larger canvas with a decorative border
    border_size = 40
    width, height = qr_img.size
    new_width = width + border_size * 2
    new_height = height + border_size * 2
    
    # Create a new image with a background
    if style == 'gradient' or style == 'gradient_vertical' or style == 'gradient_radial':
        # Create gradient background
        base_img = Image.new('RGB', (new_width, new_height), color="#f8f9fa")
        draw = ImageDraw.Draw(base_img)
        
        # Draw a gradient border
        for i in range(border_size):
            if style == 'gradient':
                r = int(80 + (175 * i / border_size))
                g = int(100 + (155 * i / border_size))
                b = int(200 - (100 * i / border_size))
            elif style == 'gradient_vertical':
                r = int(255 - (175 * i / border_size))
                g = int(200 - (100 * i / border_size))
                b = int(100 + (155 * i / border_size))
            else:  # radial
                r = int(100 + (155 * i / border_size))
                g = int(200 - (100 * i / border_size))
                b = int(255 - (175 * i / border_size))
                
            draw.rectangle([i, i, new_width - i, new_height - i], outline=(r, g, b), width=1)
    else:
        # Solid color background
        base_img = Image.new('RGB', (new_width, new_height), color="#f0f8ff")
        draw = ImageDraw.Draw(base_img)
        
        # Draw a decorative border
        for i in range(0, border_size, 4):
            color = (70, 130, 180) if i % 8 == 0 else (135, 206, 250)
            draw.rectangle([i, i, new_width - i, new_height - i], outline=color, width=2)
    
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
