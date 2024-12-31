from flask import Blueprint, render_template, request, jsonify
from app.intel import PersonIntel

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        name = data.get('name', '')
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
            
        intel = PersonIntel()
        results = intel.gather_all_info(name)
        
        # Add debugging print
        print("Search Results:", results)
        
        return jsonify(results)
    except Exception as e:
        print(f"Error in search route: {str(e)}")
        return jsonify({'error': str(e)}), 500