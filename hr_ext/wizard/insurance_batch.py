# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class InsuranceBatch(models.TransientModel):
    _name = 'insurance.batch'
    _description = 'Insurance Batch'
    
    employee_type = fields.Selection([('all employees', 'All Employees'), 
                                        ('by department', 'By Department')], 
                                        string="Employee Type")
    department_id = fields.Many2one('hr.department', string="Department ID")
    employee_line_ids = fields.One2many('insurance.batch.lines', 'insurance_batch_id')

    #when onchange the employee type data will get from either department or from employee it self
    @api.onchange('employee_type','department_id')
    def onchange_employee_type(self):
        insurance_batch_id = self.env['hr.insurance.batch'].browse(self.env.context.get('active_ids'))
        for data in self:
            employee_insurance_dict = []
            if data.employee_line_ids:
                data.employee_line_ids = [(2,employee_line.id)for employee_line in data.employee_line_ids]
            if data.employee_type == 'all employees':
                for employee_data in self.env['hr.employee'].search([]):
                    employee_insurance_dict.append({'is_employee' : True,
                                                    'employee_id' : employee_data.id,
                                                    'member_name' : employee_data.name,
                                                    'insurance_relation' : 'emp',
                                                    'policy_number' : insurance_batch_id.policy_number,
                                                    })
                    for employee_dependent_id in employee_data.dependent_ids:
                        employee_insurance_dict.append({'member_name' : employee_dependent_id.d_passport_name,
                                                        'employee_id' : employee_data.id,
                                                        'policy_number' : insurance_batch_id.policy_number,
                                                        'insurance_relation' : employee_dependent_id.passport_relation,
                                                        })

            elif data.employee_type == 'by department':
                for employee_data in self.env['hr.employee'].search([('department_id', '=', data.department_id.id)]):
                    employee_insurance_dict.append({'is_employee' : True,
                                                    'employee_id' : employee_data.id,
                                                    'member_name' : employee_data.name,
                                                    'insurance_relation' : 'emp',
                                                    'policy_number' : insurance_batch_id.policy_number,
                                                    })
                    for employee_dependent_id in employee_data.dependent_ids:
                        employee_insurance_dict.append({'member_name' : employee_dependent_id.d_passport_name,
                                                        'employee_id' : employee_data.id,
                                                        'policy_number' : insurance_batch_id.policy_number,
                                                        'insurance_relation' : employee_dependent_id.passport_relation,
                                                        })                
            data.employee_line_ids = [(0, 0, employee_insurance) for employee_insurance in employee_insurance_dict]

    #while click on Generate button
    def action_generate_insurance(self):
        if not self.employee_type:
            raise ValidationError(_("Kindly Select Employee Type to Proceed \n Else press Cancel button to Ignore"))
        for data in self.employee_line_ids:
            if not data.policy_number or not data.classes:
                raise ValidationError(_("Kindly Enter Required Data...!"))
        insurance_batch_id = self.env['hr.insurance.batch'].browse(self.env.context.get('active_ids'))
        for data in self.employee_line_ids:
            insurance_id = self.env['hr.insurance'].create(
                                                           {'is_employee' : True if data.insurance_relation == 'emp' else False,
                                                            'policy_number' : data.policy_number,
                                                            'insurance_member_emp' : data.member_name,
                                                            'classes'  : data.classes,
                                                            'insurance_relation' : data.insurance_relation,
                                                            'hr_insurance_batch_id' : insurance_batch_id.id,
                                                            'insurance_company' : insurance_batch_id.insurance_company_name,
                                                            'start_date' : insurance_batch_id.start_date,
                                                            'end_date' : insurance_batch_id.end_date,
                                                            'insurance_member_non_emp' : data.employee_id.id
                                                           })
        insurance_batch_id.write({'state' : 'Done'})
        return True

class InsuranceBatchLines(models.TransientModel):
    _name = 'insurance.batch.lines'
    _description = 'Insurance Batch Lines'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    member_name = fields.Char(string="Member Name")
    policy_number = fields.Char(string="Insurance Policy Number")
    classes = fields.Selection([('vip', 'VIP'), ('a', 'A'), ('b', 'B'), ('c', 'C')])
    is_employee = fields.Boolean(string="Is Employee?")
    insurance_batch_id = fields.Many2one('insurance.batch', string="Insurance Batch")
    insurance_relation = fields.Selection([('wife','Wife'),
                                              ('son', 'Son'),
                                              ('daug', 'Daughter'),
                                              ('emp', 'Employee')],
                                              string="Insurance Relation")
