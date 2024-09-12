# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class ProvisionCreate(models.TransientModel):
    _name = "provision.create"
    _description = "Provision Create"
    
    department_id = fields.Many2one('hr.department','Department')
    type = fields.Selection([('all','All'),('specific','Specific')],string="Type")
    employee_ids = fields.Many2many('hr.employee',string="Employee")
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    
    def _check_date(self):
        if self.start_date and self.end_date:
            end_date = (self.start_date + relativedelta(months=12)) - relativedelta(days=1)
            if self.end_date == end_date:
                return True
            else:
                raise UserError(_("The interval between the two dates should be 1 year"))
    
    def _get_employee(self):
        employee_ids = False
        if self.type == 'all':
            employee_ids = self.env['hr.employee'].search([('department_id','=',self.department_id.id)])
        elif self.type == 'specific':
            employee_ids = self.employee_ids
        if employee_ids:
            return [x.id for x in employee_ids]
        else:
            raise UserError(_('No one Employee Found.'))

    def action_create_provision(self):
        ProvisionObj = self.env['account.provision']
        if self._check_date():
            args = [self.start_date,self.end_date,self._get_employee()]
            ProvisionObj._action_create_provision(args)
