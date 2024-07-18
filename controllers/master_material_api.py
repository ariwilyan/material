from odoo import http
from odoo.http import request, Response, JsonRequest
from datetime import date, datetime
try:
    import simplejson as json
except ImportError:
    import json
import logging
import werkzeug.wrappers
import functools

_logger = logging.getLogger(__name__)

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (bytes, bytearray)):
            return obj.decode('utf-8')
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)
    
class JsonRequestPatch(JsonRequest):
    def _json_response(self, result=None, error=None):
        default_code = 200
        mime = 'application/json'
        response = {}
        
        if error is not None:
            response = error
        if result is not None:
            response = result

        body = json.dumps(response)

        return Response(
            body,
            status=error and error.pop('http_status', default_code) or default_code,
            headers=[('Content-Type', mime), ('Content-Length', len(body))]
        )

def valid_response_api(status, data, message='Success'):
    response = {
        'status': 1,
        'message': message,
        'code': status,
        'data': data
    }
    if request.httprequest.content_type == 'application/json':
        request._json_response = JsonRequestPatch._json_response.__get__(request)
        return response
    
    return werkzeug.wrappers.Response(
        status=status,
        content_type='application/json; charset=utf-8',
        response=json.dumps(response, cls=JSONEncoder),
    )

def invalid_response_api(status, error, info, message=None):
    message = message
    if not message:
        message = 'Failed'
    if 'opt' in str(info) or 'syntax' in str(info):
        info = 'Error !, Tolong hubungi administrator jika dirasa tidak terdapat kesalahan.'
    response = {
        'status': 0,
        'message': message,
        'code': status,
        'data': {
            'error': error,
            'error_descrip': info
        }
    }
    if request.httprequest.content_type == 'application/json':
        request._json_response = JsonRequestPatch._json_response.__get__(request)
        return response
    
    return werkzeug.wrappers.Response(
        status=status,
        content_type='application/json; charset=utf-8',
        response=json.dumps(response),
    )

def invalid_token():
    info = 'Token is expired or invalid!'
    error = 'invalid_token'    
    _logger.error('Token is expired or invalid!')
    return invalid_response_api(400, error, info)

def check_valid_token(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        # dummy access_token
        valid_token = 'vPaT2TbrqXP1cAbsN3kYljcbQE4dos'
        access_token = request.httprequest.headers.get('access_token')
        method = request.httprequest.method
        if not access_token:
            info = 'Missing access token in request header! >>> %s' % str(request.httprequest.headers)
            error = 'access_token_not_found'
            _logger.error(info)
            return invalid_response_api(400, error, info)
        if access_token != valid_token:
            return invalid_token()
        return func(self, *args, **kwargs)
    return wrap

class ControllerREST(http.Controller):
    @http.route('/api/keda-tech/v1/material/master_material', methods=['GET'], type='http', auth='none', csrf=False)
    @check_valid_token
    def get_master_material(self, **params):
        id = params.get('id')
        material_type = params.get('material_type')
        filter = []
        if id and id.isdigit():
            filter = [('id','=',id)]
        if material_type:
            if material_type not in ('fabric','jeans','cotton'):
                info = 'Material Type hanya bisa diisi Fabric, Jeans atau Cotton'
                error = 'invalid_input'
                _logger.error(info)
                return invalid_response_api(400, error, info)
            filter = [('material_type','=',str(material_type).lower())]
            
        if filter:
            material_obj = request.env['master.material'].sudo().search(filter, limit=1)
        else:
            material_obj = request.env['master.material'].sudo().search(filter)
        
        data = []
        for master in material_obj:
            data.append({
                'material_id': master.id,
                'material_name': master.material_name,
                'material_code': master.material_code,
                'material_type': master.material_type.title(),
                'material_buy_price': master.material_buy_price,
                'supplier_id': master.supplier_id.id,
                'supplier_code': master.supplier_id.default_code,
                'supplier_name': master.supplier_id.name
            })

        return valid_response_api(200, data)
        
    @http.route('/api/keda-tech/v1/material/master_material', methods=['POST'], type='json', auth='none', csrf=False)
    @check_valid_token
    def post_master_material(self, **post):
        if not post:
            post = request.jsonrequest
        datas = post.get('data')
        result = []
        if not datas:
            info = 'Data wajib ada !'
            error = 'empty_data'
            _logger.error(info)
            return invalid_response_api(400, error, info)
        
        for data in datas:
            mandatory_fields = ['material_name', 'material_code', 'material_type', 'material_buy_price', 'supplier_code']
            fields = []
            for mandatory in mandatory_fields:
                if mandatory not in data.keys():
                    fields.append(mandatory)

            if len(fields) > 0:
                info = 'Mandatory Request in Body %s!' % (fields)
                error = 'error_mandatory_params'
                return invalid_response_api(400, error, info)
            
            material_name = data.get('material_name')
            material_code = data.get('material_code')
            material_type = data.get('material_type')
            material_buy_price = data.get('material_buy_price')
            supplier_code = data.get('supplier_code')

            if not str(material_buy_price).isdigit():
                info = 'Data Material Buy Price harus digit'
                error = 'invalid_input'
                return invalid_response_api(400, error, info)
            if int(material_buy_price) < 100:
                info = 'Data Material Buy Price tidak boleh kurang dari 100 untuk material code %s' % (str(material_code))
                error = 'invalid_input'
                return invalid_response_api(400, error, info)
            
            if material_type.lower() not in ('fabric','jeans','cotton'):
                info = 'Material Type hanya bisa diisi Fabric, Jeans atau Cotton untuk material code %s' % (str(material_code))
                error = 'invalid_input'
                return invalid_response_api(400, error, info)
            
            supplier_obj = request.env['res.partner'].sudo().search([('default_code','=',supplier_code)], limit=1)
            if not supplier_obj:
                info = 'Pastikan Supplier %s telah terdaftar di Master Supplier' % (str(supplier_code))
                error = 'data_not_found'
                return invalid_response_api(400, error, info)

            duplicate_material_obj = request.env['master.material'].sudo().search([('material_code','=',material_code)], limit=1)
            if duplicate_material_obj:
                info = 'Master Material dengan Code %s sudah ada' % (material_code)
                error = 'duplicate_transaction'
                return invalid_response_api(400, error, info)
                
            try:
                material_obj = request.env['master.material'].sudo().create({
                    'material_name': material_name,
                    'material_code': material_code,
                    'material_type': material_type.lower(),
                    'material_buy_price': material_buy_price,
                    'supplier_id': supplier_obj.id
                })
                result.append({
                    'material_id': material_obj.id,
                    'material_name': material_obj.material_name,
                    'material_code': material_obj.material_code
                })
            except Exception as err:
                info = 'Error : %s' % (str(err[0]))
                error = 'Gagal Create Master Material'
                return invalid_response_api(500, error, info)
            
        return valid_response_api(200, result, message='Success Create Material')
        
    @http.route('/api/keda-tech/v1/material/master_material', methods=['PUT'], type='json', auth='none', csrf=False)
    @check_valid_token
    def put_master_material(self, **put):
        if not put:
            put = request.jsonrequest
        id = put.get('material_id')
        if not id or not str(id).isdigit():
            info = 'Mandatory Request in Body id!'
            error = 'error_mandatory_params'
            _logger.error(info)
            return invalid_response_api(400, error, info)
        
        supplier_obj = False
        supplier_code = put.get('supplier_code')
        if supplier_code:
            supplier_obj = request.env['res.partner'].sudo().search([('default_code','=',supplier_code)], limit=1)
            if not supplier_obj:
                info = 'Pastikan Supplier %s telah terdaftar di Master Supplier' % (str(supplier_code))
                error = 'data_not_found'
                return invalid_response_api(400, error, info)

        vals = {}
        material_obj = request.env['master.material'].sudo().search([('id','=',id)], limit=1)
        if not material_obj:
            info = 'Master Material dengan id %s tidak ada' % (str(id))
            error = 'data_not_found'
            return invalid_response_api(400, error, info)
        
        if put.get('material_name'):
            vals.update({'material_name': put.get('material_name')})
        if put.get('material_code'):
            vals.update({'material_code': put.get('material_code')})
        if put.get('material_type'):
            material_type = put.get('material_type')
            if material_type.lower() not in ('fabric','jeans','cotton'):
                info = 'Material Type hanya bisa diisi Fabric, Jeans atau Cotton untuk material id %s' % (str(id))
                error = 'invalid_input'
                return invalid_response_api(400, error, info)
            vals.update({'material_type': put.get('material_type')})
        if put.get('material_buy_price'):
            material_buy_price = put.get('material_buy_price')
            if not str(material_buy_price).isdigit():
                info = 'Data Material Buy Price harus digit'
                error = 'invalid_input'
                return invalid_response_api(400, error, info)
            if int(material_buy_price) < 100:
                info = 'Data Material Buy Price tidak boleh kurang dari 100 untuk material id %s' % (str(id))
                error = 'invalid_input'
                return invalid_response_api(400, error, info)
            vals.update({'material_buy_price': put.get('material_buy_price')})
        if supplier_obj:
            vals.update({'supplier_id': supplier_obj.id})

        try:
            material_obj.sudo().write(vals)
            data = {'material_id': id}
            return valid_response_api(200, data, message='Success Update Material')
        except Exception as err:
            info = 'Error : %s' % (str(err[0]))
            error = 'Gagal Update Master Material'
            return invalid_response_api(500, error, info)
        
    @http.route('/api/keda-tech/v1/material/master_material', methods=['DELETE'], type='json', auth='none', csrf=False)
    @check_valid_token
    def delete_master_material(self, **delete):
        if not delete:
            delete = request.jsonrequest
        id = delete.get('material_id')
        if not id or not str(id).isdigit():
            info = 'Mandatory Request in Body id!'
            error = 'error_mandatory_params'
            _logger.error(info)
            return invalid_response_api(400, error, info)
        
        material_obj = request.env['master.material'].sudo().search([('id','=',id)], limit=1)
        if not material_obj:
            info = 'Master Material dengan id %s tidak ada' % (str(id))
            error = 'data_not_found'
            return invalid_response_api(400, error, info)
        
        try:
            material_obj.sudo().unlink()
            data = {'material_id': id}
            return valid_response_api(200, data, message='Success Delete Material')
        except Exception as err:
            info = 'Error : %s' % (str(err[0]))
            error = 'Gagal Delete Master Material'
            return invalid_response_api(500, error, info)