# -*- coding: utf-8 -*-

from odoo import models, api, fields, _


class CustomerReport(models.TransientModel):
    _name = "customer.report.wizard"
    _description = "Customer Report Wizard"

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
        return self.env.ref('customer_report.cr_report').report_action(self, data=datas)
