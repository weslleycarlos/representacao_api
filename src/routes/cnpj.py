from flask import Blueprint, jsonify, request
import requests

cnpj_bp = Blueprint('cnpj', __name__)

@cnpj_bp.route('/consultar', methods=['POST'])
def consultar_cnpj():
    """Consulta dados de CNPJ usando a API ReceitaWS"""
    try:
        data = request.json
        
        if not data or not data.get('cnpj'):
            return jsonify({'error': 'CNPJ é obrigatório'}), 400
        
        cnpj = data['cnpj'].replace('.', '').replace('/', '').replace('-', '')
        
        if len(cnpj) != 14 or not cnpj.isdigit():
            return jsonify({'error': 'CNPJ inválido'}), 400
        
        # Consulta na API ReceitaWS
        url = f'https://www.receitaws.com.br/v1/cnpj/{cnpj}'
        
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return jsonify({'error': 'Erro ao consultar CNPJ'}), 500
        
        data = response.json()
        
        if data.get('status') == 'ERROR':
            return jsonify({'error': data.get('message', 'CNPJ não encontrado')}), 404
        
        return jsonify({
            'cnpj': data.get('cnpj', ''),
            'razao_social': data.get('nome', ''),
            'nome_fantasia': data.get('fantasia', ''),
            'situacao': data.get('situacao', ''),
            'atividade_principal': data.get('atividade_principal', [{}])[0].get('text', '') if data.get('atividade_principal') else ''
        }), 200
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Timeout na consulta do CNPJ'}), 408
    except requests.exceptions.RequestException:
        return jsonify({'error': 'Erro de conexão ao consultar CNPJ'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

