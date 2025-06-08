from flask import jsonify
from flask_login import login_required
from . import api_bp

@api_bp.route('/predict', methods=['POST'])
@login_required
def predict():
    # Tahmin işlemleri burada yapılacak
    return jsonify({
        'success': True,
        'message': 'Tahmin başarıyla tamamlandı',
        'data': {}
    })
