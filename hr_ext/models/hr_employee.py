# -*- coding: utf-8 -*-

import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class InheritHrEmployee(models.Model):
    # Private attributes
    _inherit = 'hr.employee'

    # Fields declaration
    timesheet_manager_id = fields.Many2one(
        'res.users', string='Timesheet Responsible',
        domain=lambda self: [],
        help="User responsible of timesheet validation. Should be Timesheet Manager.")
    expense_manager_id = fields.Many2one(
        'res.users', string='Expense Responsible',
        domain=lambda self: [],
        help="User responsible of expense approval. Should be Expense Manager.")
    joining_date = fields.Date("Date of Join")
    # total_years = fields.Char("Total Years/Days", compute="_compute_dateofjoin")
    religion = fields.Selection([('Muslim', 'Muslim'), ('NonMuslim', 'Non Muslim')], string="Religion")
    dependent = fields.Boolean("Have Dependent?")
    emp_iqama = fields.Many2one('hr.iqama', string="Iqama Number")
    passport = fields.Many2one('hr.passport', string="Passport")
    doc_type = fields.One2many('hr.emp.doc', 'hrdoc', string="Doc Type")
    insurance = fields.One2many('hr.insurance', 'insurance_member_non_emp', string="Employee Insurance")
    emp_access_mgt = fields.One2many('hr.emp.access.mgt', 'access_emp', string="Management Assets")
    family_employee = fields.One2many('hr.iqama.family', 'hife', string="Family Iqama")
    emergency = fields.One2many('hr.emergency.contact', 'emergency_employee', string="Emergency Contacts")
    education = fields.One2many('hr.education', 'education_emp', string="Education")
    job_pos = fields.Char(string='Job Positions', related="job_id.name")
    country_name = fields.Char(related="country_id.name", string="Country Name")
    national_id = fields.Many2one('hr.nationality', string="National ID")
    bank_id = fields.Many2one('res.bank', string="Bank Name")
    iban = fields.Char(string="IBAN")
    swift_code = fields.Char("Swift Code", related="bank_id.bic")
    # bank_name = fields.Char("Bank Name", related="bank_id.bank_name")
    arabic_name = fields.Char("Arabic Name")
    job_id = fields.Many2one('hr.job', 'Job Position', required=False)
    ext_no = fields.Char("Extension No")
    dependent_ids = fields.One2many('hr.passport', 'd_emp')
    work_permit = fields.One2many('work.permit', 'employee', string="Work Permit Ids")
    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('submit', 'Approved')], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3,
    #     default='draft')
    # active = fields.Boolean('Active', related='resource_id.active', default=False, store=True, readonly=False)
    # show_dpt_btn = fields.Boolean(compute="_get_manager", oldname="new_manager")
    # current_leave_state = fields.Selection(selection_add=[('initial', 'Initial')])
    user_id = fields.Many2one('res.users', 'User', store=True, readonly=False)
    sponsor_id = fields.Many2one('hr.sponsor', 'Sponsor', readonly=False)
    # establ_labor_off_no = fields.Char("Establ Labor Office No", related="sponsor_id.establ_labor_off_no")
    prof_office_work = fields.Char('Profession In Office Work')
    company_name = fields.Char(related="company_id.name", string='Company Name', store=True)
    profession = fields.Char('Profession')
    kingdom_entry_date = fields.Char('Kingdom Entry Date')
    iqama_no = fields.Char('Iqama No')
    issue_date_iqama = fields.Date('Issuance Date Iqama')
    insur_sub_no = fields.Char('Insurance Subscription No.')
    worker_no = fields.Char('Worker No.')
    # establish_no = fields.Char('Establish No.')
    border_no = fields.Char('Border No.')
    # employer_no = fields.Char('Employer No.')
    sponser_name = fields.Char('Sponsor Name')
    status = fields.Selection([('OnDuty', 'On Duty'), ('Long Leave', 'Long Leave')], string="Status", )
    payment_type = fields.Selection([('Bank', 'Bank'), ('Cash', 'Cash')], string="Payment Type", )
    kingdom_status = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Kingdom Staus", )
    account_no = fields.Char('Account No')
    employee_category = fields.Many2one('employee.category', string='Category')
    account_payable_id = fields.Many2one('account.account', string='Payable Account')
    account_receivable_id = fields.Many2one('account.account', string='Receivable Account')
    iqama_expiry = fields.Date(related='emp_iqama.expiry_date', string="Iqama Expiry Data")
    passport_issue_date = fields.Date(related='passport.passport_issue_date')
    passport_expiry = fields.Date(related='passport.expiry_date', string="Passport Expiry Date")
    analytic_account = fields.Many2one('account.analytic.account', string="Analytic Account", )
    local_transfer = fields.Boolean('Local Transfer')
    sponsor_number = fields.Integer(related='sponsor_id.sponsor_id')
    sponsor_phone = fields.Integer(related='sponsor_id.Phone')
    sponsor_email = fields.Char(related='sponsor_id.email')

    employee_type = fields.Selection([
        ('employee', 'Employee'),
        ('student', 'Student'),
        ('trainee', 'Trainee'),
        ('internal', 'Internal'), 
        ('outsource', 'Outsource'),
        ('contractual', 'Contractual'),
        ('contractor', 'Contractor'),
        ('freelance', 'Freelancer'),
        ], string='Employee Type', default='employee', 
        help="The employee type. Although the primary purpose may seem to categorize employees, this field has also an impact in the Contract History. Only Employee type is supposed to be under contract and will have a Contract History.")

    # employee_type = fields.Selection(selection_add=
    #     [ ('contractual', 'Contractual')],default="employee", ondelete='cascade')
    no_of_dependent = fields.Integer(compute="compute_no_of_dependent")
    blood_group = fields.Selection([
        ('A+','A+'),
        ('B+','B+'),
        ('A-','A-'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),

    ],string="Blood Group")
    job_title_ar = fields.Char()
    work_location_ar = fields.Char()
    gosi_no = fields.Integer("Gosi No")
    gosi_reg_date = fields.Date('Gosi Registration date')
    level = fields.Many2one('hr.policies',required=0)
    grading = fields.Many2one('hr.grading',required=0)
    employee_number = fields.Char("Employee Number")
    old_employee_number = fields.Char("Old Employee Number")


    #make validation based if related user set than can't make private address changed
    # def write(self, vals):

    #     res = super(InheritHrEmployee, self).write(vals)
    #     for data in self:
    #         if data.user_id and vals.get('address_home_id') and not vals.get('user_id'):
    #             raise UserError(_('You Can not Change Private Address if Related User is set...!'),)
    #     return res

    # @api.constrains('address_home_id')
    # def _check_address_home_id(self):
    #     print ("\n\nt\ self",self.address_home_id,self.user_id)
    #     SL

    #if not loaded private infoamtion than load that data too
    @api.onchange('user_id')
    def onchange_user_id(self):
        for data in self:
            if data.user_id and not data.address_home_id:
                data.address_home_id = data.user_id.partner_id.id

    # compute and search fields, in the same order of fields declaration
    @api.depends('dependent_ids')
    def compute_no_of_dependent(self):
        """return the number of departments"""
        for rec in self:
            count = 0
            if rec.dependent_ids:
                for i in rec.dependent_ids:
                    count = count + 1
            rec.no_of_dependent = count

    # def _compute_dateofjoin(self):
    #     """
    #     it return the old employee name and attach partner when we change related user
    #     """
    #     if self.joining_date:
    #         date_today = datetime.today().strftime('%Y-%m-%d')
    #         day_from = fields.Datetime.from_string(self.joining_date)
    #         day_to = fields.Datetime.from_string(date_today)
    #         nb_of_days = (day_to - day_from).days + 1
    #         difference_in_years = relativedelta(day_to, day_from).years
    #         if (difference_in_years < 1):
    #             self.totalyears = str(nb_of_days) + 'days (' + str(relativedelta(day_to, day_from).months) + ')'
    #         else:
    #             self.totalyears = str(difference_in_years) + ' years'

    # Constraints and onchanges
    @api.onchange('employee_type')
    def onchange_employee_type(self):
        """generate sequence on base of employee type"""
        if self.employee_type:
            if self.employee_type == 'internal':
                self.employee_number = self.env['ir.sequence'].next_by_code('employee.internal')
            if self.employee_type == 'outsource':
                self.employee_number = self.env['ir.sequence'].next_by_code('employee.outsource')
            if self.employee_type == 'contractual':
                self.employee_number = self.env['ir.sequence'].next_by_code('employee.contractual')

    @api.onchange('user_id')
    def _onchange_user(self):
        """
        it return the old employee name and attach partner when we change related user
        """
        address_home_id = self.address_home_id
        old_name = self.name
        res = super(InheritHrEmployee, self)._onchange_user()
        self.address_home_id = address_home_id
        self.name = old_name
        return res

    # @api.onchange('country_id')
    # def on_change_country(self):
    #     """
    #     it check the country code of KSA and eraise error
    #     """
    #     if self.country_id.code == 'SA':
    #         if self.emp_iqama:
    #             raise UserError(_('Employee is a not a Saudi National'))
    #     else:
    #         if self.national_id:
    #             raise UserError(_('Employee is a Saudi National'))

    # CRUD methods (and name_get, name_search, ...) overrides
    @api.model
    def create(self, vals):
        emp_name = vals.get('name')
        HrEmployeeObj = super(InheritHrEmployee, self).create(vals)
        customer_id = self.env['res.partner'].create({'name': emp_name})
        HrEmployeeObj.address_home_id = customer_id
        HrEmployeeObj.name = emp_name
        HrEmployeeObj.address_home_id.employee = True
        HrEmployeeObj.address_home_id.active = True
        HrEmployeeObj.address_home_id.property_account_payable_id = HrEmployeeObj.account_payable_id.id
        HrEmployeeObj.address_home_id.property_account_receivable_id = HrEmployeeObj.account_receivable_id.id
        return HrEmployeeObj

    # def write(self, values):
    #     if 'bank_id' in values:
    #         if self.env.user.has_group('hr_ext.group_bank_admin'):
    #             return super(InheritHrEmployee, self).write(values)
    #         else:
    #             raise UserError(_("You can't edit bank details"))
    #     else:
    #         return super(InheritHrEmployee, self).write(values)

    def create_private_address(self):
        """
        it check the private address on employee if it  not exist then it creates
        """
        employees = self.env['hr.employee'].search([('address_home_id', '=', False)])
        for i in employees:
            if not i.user_id:
                partner_id = self.env['res.partner'].create({'name': i.name})
                i.address_home_id = partner_id
            else:
                i.address_home_id = i.user_id.partner_id

    # def _sync_user(self, user):
    #     if self.name:
    #         return {}
    #     else:
    #         return super(InheritHrEmployee, self)._sync_user(user)

class WorkPermit(models.Model):
    # Private attributes
    _name = 'work.permit'
    _description = 'WorkPermit'

    # Fields declaration
    visa_no = fields.Char('Visa No', required=1)
    workpermit_no = fields.Char('Work Permit No')
    visa_expiry_date = fields.Char('Visa Expiry Date')
    employee = fields.Many2one('hr.employee')


class EmployeeCategory(models.Model):
    # Private attributes
    _name = "employee.category"
    _description = "Employee Category"

    # Fields declaration
    name = fields.Char(required=1)


class HrJob(models.Model):
    # Private attributes
    _inherit = 'hr.job'

    # Fields declaration
    job_title_ar = fields.Char()