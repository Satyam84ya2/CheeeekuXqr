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

# Handle CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(debug=True)
