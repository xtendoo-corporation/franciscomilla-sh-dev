from odoo import models, fields

class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    kg_price = fields.Float(string='Precio por kg')
