# -*- coding: utf-8 -*-

import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrNationalId(models.Model):
    _name = 'hr.nationality'
    _description = "National IDs"
    _rec_name = "nationality_name"

    id = fields.Many2one('hr.id.type',string="ID Type")
    nationality_name = fields.Char('ID No.',required=True)
    employee = fields.Many2one('hr.employee',string="Employee",required=True)
    issue_date = fields.Date("Issue date")
    expiry_date = fields.Date("Expiry date")
    date_of_birth = fields.Date("Date of Birth",related="employee.birthday")
    place_of_issue = fields.Char("Place of Issue")
    x_emp_id = fields.Char('Employee Number')
    department = fields.Many2one('hr.department',string="Department",related="employee.department_id")
    blood_group = fields.Selection(string="Blood Group",related="employee.blood_group")
    dependent = fields.Boolean("Dependent")
    family = fields.One2many('hr.iqama.family', 'nif', string="Family Iqama")

    @api.onchange('nationality_name')
    def national_id_regex(self):
        """it check the nationality and limit to iqama numbers """
        if(self.nationality_name):
            result = re.match('^(1)[0-9]?', self.nationality_name, flags=0)
            if(len(self.nationality_name) != 10):
                raise UserError(_('Invalid Entry. Entry should contain complete 10 numbers'))
            if result:
                pass
            else:
                raise UserError(_('Invalid National ID Entry. Entry should start from 1'))

    @api.constrains('employee')
    def place_employee_nationality(self):
        if self.employee.country_id.code == 'SA':
            self.env['hr.employee'].search([('id', '=', self.employee.id)]).update(
                {'national_id': self.id})
        else:
            raise UserError(_('Employee is not a Saudi National'))

    _sql_constraints = [('nationality_name_uniq', 'unique (nationality_name)',
                         'National ID is already existed!')]


class IdType(models.Model):
    _name = 'hr.id.type'
    _description = "ID Type"

    name = fields.Char("ID Type", required=1)
