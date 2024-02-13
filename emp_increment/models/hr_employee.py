# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    increment_line = fields.One2many('emp.increment', 'employee_id', 'Increment')
    five_year_provision = fields.Boolean(default=False)

    # Action open provision
    def action_open_increment(self):
        context = {'default_employee_id' : self.id}
        return {
            'name': _('Increment'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'emp.increment',
            'view_id': False,
            'context'  : context,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.increment_line.ids)],
        }
