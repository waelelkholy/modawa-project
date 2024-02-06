# -*- coding: UTF-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    sh_sec_qty = fields.Float('Secondary Qty', readonly=True)
    sh_sec_uom = fields.Many2one("uom.uom", "Secondary UOM", readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['sh_sec_uom'] = "l.sh_sec_uom"
        res['sh_sec_qty'] = "SUM(l.sh_sec_qty / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END)"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            l.sh_sec_uom"""
        return res


class PurchaseReport(models.Model):
    _inherit = 'purchase.report'

    sh_sec_qty = fields.Float('Secondary Qty', readonly=True)
    sh_sec_uom = fields.Many2one("uom.uom", "Secondary UOM", readonly=True)

    def _select(self):
        return super(PurchaseReport, self)._select() + ", l.sh_sec_uom as sh_sec_uom" + ", sum(l.sh_sec_qty/line_uom.factor*product_uom.factor) as sh_sec_qty"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", l.sh_sec_uom"
