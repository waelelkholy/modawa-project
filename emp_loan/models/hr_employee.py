# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm
from odoo.exceptions import UserError, ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    def show_loans(self):
        return {
            'name': _('Employee Loan'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.loan',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('employee_id', '=', self.ids)],
        }