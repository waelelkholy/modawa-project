from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    recipe_id = fields.Many2one('sale.line.recipe')
