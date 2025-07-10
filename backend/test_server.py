from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    # This creates a JSON response
    response = jsonify({"status": "ok, the test server is working"})
    
    # This header explicitly gives permission to everyone, just for this test
    response.headers.add('Access-Control-Allow-Origin', '*')
    
    return response

if __name__ == '__main__':
    print("🚀 Starting simple test server on http://localhost:8888")
    app.run(debug=True, port=8888) # Changed to 8888