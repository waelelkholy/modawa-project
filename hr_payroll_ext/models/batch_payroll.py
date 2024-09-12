# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    is_payslip_approve = fields.Boolean(string="Is Approved", compute="_compute_payslip_approval")

    #compute filed for payslip data conditon
    def _compute_payslip_approval(self):
        for data in self:
            if data.state == 'verify':
                if any(line.state != 'verify' for line in data.slip_ids):
                    data.is_payslip_approve = False
                else:
                    data.is_payslip_approve = True
            else:
                data.is_payslip_approve = False


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    # all_emp = fields.Boolean(default=True)
    # options = fields.Selection(
    #     [('all', 'All Employee'), ('dept', 'Department')], default='all', string ='Options')
    # is_show_dept = fields.Boolean()
    # department_id = fields.Many2one('hr.department')
    # emp_type = fields.Selection(
    #     [('internal', 'Internal'), ('outsource', 'Outsource'), ('contractual', 'Contractual')],default='internal', string ='EmployeeType')

    # @api.onchange('emp_type','options','department_id','structure_id')
    # def onchange_get_employees(self):
    #     self.employee_ids = False
    #     domain = []
    #     if self.options == 'all':
    #         self.department_id = False
    #     if self.emp_type:
    #         domain += [('employee_type', '=', self.emp_type)]
    #     if self.department_id:
    #         domain += [('department_id', '=', self.department_id.id)]
    #     if self.structure_id:
    #         domain += [('contract_id.state', '=', 'open')]
    #     employee_ids = self.env['hr.employee'].search(domain)
    #     self.employee_ids = employee_ids.ids


    def compute_sheet(self):
        res = super(HrPayslipEmployees, self).compute_sheet()
        for data in self.employee_ids:
            if not data.contract_id:
                raise UserError(_("Contract of Employee %s Not Founded....!") % (data.name))
            if data.contract_id and data.contract_id.state != 'open':
                raise UserError(_("Contract of Employee %s Is not in Running Stage....!") % (data.name))
        if 'res_id' in res:
            batch_payslip = self.env['hr.payslip.run'].search([('id','=',res['res_id'])],limit=1)
            for i in batch_payslip.slip_ids:
                i.state = 'hr'
                i._onchange_employee()
                i.compute_sheet()
        return res
