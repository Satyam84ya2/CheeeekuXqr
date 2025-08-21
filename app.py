from flask import Flask, request, send_file, jsonify
import qrcode
import io

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "UPI QR Code Generator API",
        "usage": {
            "without_amount": "/api/qr",
            "with_amount": "/api/qr?amount=100",
            "with_custom_name": "/api/qr?amount=100&name=YourName",
            "with_currency": "/api/qr?amount=100&currency=INR"
        },
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
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(upi_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save image to bytes buffer
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Return the image
        return send_file(img_buffer, mimetype='image/png', 
                         as_attachment=False, 
                         download_name='upi_qr.png')
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Handle CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(debug=True)
