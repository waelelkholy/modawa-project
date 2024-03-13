from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    recipe_id = fields.Many2one('sale.line.recipe')

    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        if self.recipe_id:
            if self.recipe_id.state != 'approve':
                raise ValidationError(_(
                    "You can't confirm because you recipe not approved yet"
                ))
        return res
