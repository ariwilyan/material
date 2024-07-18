# 1: imports of python lib
from datetime import timedelta, datetime, date

# 2: import of known third party lib

# 3:  imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError

# 4:  imports from odoo modules

# 5: local imports

# 6: Import of unknown third party lib


class MasterMaterial(models.Model):
    _name = "master.material"
    _order = "id DESC"
    _description = "Master Material"

    material_code = fields.Char('Material Code', required=True)
    material_name = fields.Char('Material Name', required=True)
    material_buy_price = fields.Integer('Material Buy Price', required=True)

    # Selection Fields 
    material_type = fields.Selection([
        ('fabric', 'Fabric'),
        ('jeans', 'Jeans'),
        ('cotton', 'Cotton')
    ], string='Material Type', required=True)

    # Relation Fields
    supplier_id = fields.Many2one('res.partner', string='Nama Supplier', required=True)

    # constraints & sql constraints
    @api.constrains('material_buy_price')
    def _validate_material_buy_price(self):
        if self.material_buy_price < 100:
            raise ValidationError(_('Material Buy Price tidak boleh kurang dari 100 !'))
    
    # override methods
    def name_get(self):
        if self._context is None:
            self._context = {}
        res = []
        for record in self:
            title = "Material [%s - %s]" % (record.material_code.upper(), record.material_name.title())
            res.append((record.id, title))
        return res
        
    # action methods
    def action_master_material_tree(self):
        tree_view_id = self.env.ref('master_material.view_master_material_tree').id
        form_view_id = self.env.ref('master_material.view_master_material_form').id
        search_view_id = self.env.ref('master_material.view_master_material_search').id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Master Material',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'master.material',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'search_view_id': search_view_id,
            'context': {
                'readonly_by_pass': 1
            }
        }