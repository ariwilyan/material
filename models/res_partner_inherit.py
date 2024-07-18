# 1: imports of python lib

# 2: import of known third party lib

# 3:  imports of odoo
from odoo import models, fields, api, _

# 4:  imports from odoo modules

# 5: local imports

# 6: Import of unknown third party lib


class Partner(models.Model):
    _inherit = "res.partner"
    _description = "Res Partner Inherit"

    default_code = fields.Char('Default Code')
    rel_code = fields.Char('Rel Code')
    is_finco = fields.Boolean('Is Finco')