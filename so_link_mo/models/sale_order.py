from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    manufacturing_order_ids = fields.Many2many('mrp.production')
    manufacturing_order_count = fields.Integer(compute='compute_manufacturing_order_count')
    create_mo = fields.Boolean()

    def compute_manufacturing_order_count(self):
        for rec in self:
            if rec.manufacturing_order_ids:
                rec.manufacturing_order_count = len(rec.manufacturing_order_ids)
            else:
                rec.manufacturing_order_count = 0

    def button_manufacturing(self):
        mo_ids = self.manufacturing_order_ids.ids
        for line in self.order_line:
            if line.manufacturing_true:
                bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_id.id)])[0]
                mo = self.env['mrp.production'].create({
                    'bom_id': bom.id,
                    'product_qty': line.product_uom_qty,
                    'origin': str(self.name) + " " + line.product_id.name,
                    'date_planned_start': self.commitment_date
                })
                line.manufacturing_order_id = mo.id
                recipe = self.env['sale.line.recipe'].create({
                    'product_id': line.product_id.id,
                    'sale_id': self.id,
                    'sale_line_id': line.id,
                    'mo_id': mo.id,
                })
                mo.update({
                    'recipe_id' : recipe.id
                })
                line.update({
                    'recipe_id' : recipe.id
                })
                mo_ids.append(mo.id)
        self.manufacturing_order_ids = mo_ids
        self.create_mo = True

    def action_view_mo(self):
        result = {
            "type": "ir.actions.act_window",
            "res_model": "mrp.production",
            "domain": [('id', 'in', self.manufacturing_order_ids.ids)],
            "name": _("Manufacturing Order"),
            'view_mode': 'tree,form',
        }
        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    manufacturing_true = fields.Boolean()
    manufacturing_order_id = fields.Many2one('mrp.production')
    recipe_id = fields.Many2one('sale.line.recipe')

    def action_show_details(self):
        return {
            'name': _('recipe'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sale.line.recipe',
            'res_id': self.recipe_id.id,
            'target': 'new'

        }


class SaleLineRecipe(models.Model):
    _name = 'sale.line.recipe'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.template')
    sale_id = fields.Many2one('sale.order')
    sale_line_id = fields.Many2one('sale.order.line')
    mo_id = fields.Many2one('mrp.production')
    attachment = fields.Binary()
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved')],default='draft')

    def approve_recipe(self):
        self.state = 'approve'
