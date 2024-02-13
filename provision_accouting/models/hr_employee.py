# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    hire_date = fields.Date(string='Hire Date')
    provision_line = fields.One2many('account.provision','employee_id','Provision')
    percentages = fields.Float(string='Percentages')
    monthly_charges = fields.Float(string='Monthly Charges')
    
    # Action open provision
    def action_open_provision(self):
        return {
            'name': _('Provision'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.provision',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.provision_line.ids)],
        }
