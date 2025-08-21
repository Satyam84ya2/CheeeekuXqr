from flask import Flask, request, send_file, jsonify
import qrcode
import io

app = Flask(__name__)

@app.route('/api/qr', methods=['GET', 'OPTIONS'])
def generate_qr():
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 200
    
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

# Vercel requires a Flask app instance named "app"
# This file will be treated as a serverless function
