# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class SaleOrder(models.Model):
    # Private attributes
    _inherit = 'sale.order'

    def action_confirm(self):
        if self.partner_id:
            if self.partner_id.no_more_orders:
                raise UserError(_("This customer at no More Orders"))
        return super(SaleOrder, self).action_confirm()

