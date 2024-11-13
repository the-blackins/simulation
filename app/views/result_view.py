from flask import Flask, render_template, request, jsonify, Blueprint
import app



form_bp = Blueprint('main', __name__)

@form_bp.route('/', methods=['GET'])
def show_form():
    return render_template('index.html')

# @app.route('/api/submit-simulation', methods=['POST'])
# def submit_simulation():
#     data = request.get_json()
#     # Here you would process the form data and send it to your API
#     return jsonify({
#         'status': 'success',
#         'message': 'Simulation configuration received',
#         'data': data
#     })

