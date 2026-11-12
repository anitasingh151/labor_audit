from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/costs', methods=['GET'])
def get_costs():
    data = [{"cost_type": 2, "status": "A"}]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)

