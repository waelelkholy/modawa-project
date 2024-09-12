# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrInsuranceBatch(models.Model):
    _name = 'hr.insurance.batch'
    _description = "Insurance Insurance"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Insurance Batch Name", tracking=True)
    start_date = fields.Date("Start date", tracking=True)
    end_date = fields.Date("End date", tracking=True)
    insurance_company_name = fields.Char("Insurance Company name", tracking=True)
    state = fields.Selection([('draft','Draft'),('Done','Done')], 
    							string="State", tracking=True, default='draft')
    policy_number = fields.Char(string="Insurance Policy Number")


    #while click on Insurance Button
    def action_open_insurance(self):
        return {
            'name': _('Employee Insurance'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.insurance',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context' : {'default_insurance_company' : self.insurance_company_name, 
                        'default_start_date' : self.start_date,
                        'default_end_date' : self.end_date,
                        },
            'domain': [('hr_insurance_batch_id', '=', self.id)],
        }
