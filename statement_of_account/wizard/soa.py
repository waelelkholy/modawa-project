# -*- coding: utf-8 -*-

from odoo import models, api, fields, _


class SOA(models.TransientModel):
    _name = "soa.wizard"
    _description = "SOA Wizard"

    customer_id = fields.Many2many(comodel_name="res.partner", string="Partner")
    date_f = fields.Date("Date From", required=True)
    date_t = fields.Date("Date To", required=True)
    partner_type = fields.Boolean(default=False)
    payment_type = fields.Selection([('all','ALL'),('reconciled','Reconciled')])

    file = fields.Binary('Download Report')
    name = fields.Char()

    def generate_soa_xlsx(self):
        datas = {
            'wizard_data': self.read()
        }
        return self.env.ref('statement_of_account.soa_report').report_action(self, data=datas)
