# -*- coding: utf-8 -*-
from datetime import date
import datetime
from odoo import api, fields, models, tools,_
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import calendar


class EmpIncrement(models.Model):
    # Private Attribute
    _name = 'emp.increment'
    _description = 'Employee Increment'
    _rec_name = 'employee_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Declaring Fields
    employee_id = fields.Many2one('hr.employee', string="Employee")
    employee_no = fields.Char(string="Employee No", related="employee_id.employee_number")
    employee_old_no = fields.Char(string="Employee Old No", related="employee_id.old_employee_number")
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id")
    contract_id = fields.Many2one('hr.contract', store=True)

    start_date = fields.Date("Start Date")
    first_contract = fields.Date("First Contract")
    date_of_join = fields.Date("Date of Join")
    effective_date = fields.Date("Effective Date")
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'),
         ('done', 'Done'), ('Reject', 'Reject')], default='draft', tracking=True)

    currency_id = fields.Many2one('res.currency', string='Currency')

    # Old Monthly Advantages
    old_wage = fields.Monetary("Wage", related="employee_id.contract_id.wage")
    old_basic_salary = fields.Float("Basic Salary", store=True)
    old_basic_allowance = fields.Float("Basic Allowance")
    old_extra_allowance = fields.Float("Extra Allowance")
    old_total_deduction = fields.Float("Total Deduction")

    # New Monthly Advantages
    new_basic_salary = fields.Float("New Basic Salary", compute='_compute_new_salary', store=True)
    new_basic_allowance = fields.Float("New Basic Allowance")
    addition_type = fields.Selection([('amount', 'Amount'),
                                      ('percentage', 'Percentage')], string='Addition Type')
    percentage = fields.Float("Rate Amount in %")
    addition_value = fields.Float("Addition Value" )
    # new_basic = fields.Float("New Basic")

    old_monthly_advantages_ids = fields.One2many('old.monthly.advantages', 'old_emp_increment_id',
                                                 string='Old Monthly Advantages')

    new_monthly_advantages_ids = fields.One2many('new.monthly.advantages', 'emp_increment_id',
                                                 string='New Monthly Advantages')
    revised_wage = fields.Float('Revised Wage', compute="_compute_revised_amount")
    # backdate
    backdate_boolean = fields.Boolean("Effective in Back Date",default=False)
    backdate = fields.Date()
    reject_reason = fields.Char(string="Reject Reason")
    company_id = fields.Many2one('res.company', string="Company ID", default=lambda self:self.env.company.id)

    #override method to make restict on it
    def unlink(self):
        for data in self:
            if data.state not in ['draft']:
                raise UserError(_('You can delete only draft status records...'),)
        return super(EmpIncrement, self).unlink()

    #for making perfect amout after saving
    @api.model
    def create(self, values):
        res = super(EmpIncrement, self).create(values)
        res.onchange_addition_type()
        return res

    #when click on addition type change value on new salary one..
    @api.onchange('addition_type','percentage')
    def onchange_addition_type(self):
        for data in self:
            if data.addition_type == 'percentage' and data.percentage:
                for new_salary_rule in data.new_monthly_advantages_ids.filtered(lambda data: data.type == 'Percentage'):
                    new_salary_rule.rate = data.percentage
                    new_salary_rule.get_amount()
            elif data.addition_type == 'amount':
                for new_salary_rule in data.new_monthly_advantages_ids.filtered(lambda data: data.type == 'Amount'):
                    new_salary_rule.rate = 0
                for new_salary_rule in data.new_monthly_advantages_ids.filtered(lambda data: data.type == 'Percentage'):
                    new_salary_rule.rate = new_salary_rule.old_rate
                    new_salary_rule.get_amount()

    @api.onchange('backdate_boolean')
    def onchange_backdate(self):
        if self.backdate_boolean:
            self.effective_date = fields.Date.today()
        else:
            self.effective_date = False

    #method to pass notification to ceo user
    def _create_ceo_notification(self):
        is_employee_increment = self.env['ir.config_parameter'].sudo().get_param('emp_increment.is_employee_increment')
        if is_employee_increment:
            for data in self.env.user.company_id.employee_increment_user_ids:
                res_model_id = self.env['ir.model'].search(
                    [('name', '=', self._description)]).id
                search_mail_activity_id = self.env['mail.activity'].search([('res_id','=',self.id),('user_id','=',data.id)])
                if not search_mail_activity_id:
                    message = "Please approve the Employee Increment :-" + " " +  str(self.employee_no) + "which is created by :-" + " " +str(self.env.user.name)
                    activity_id = self.env['mail.activity'].create([{'activity_type_id': 4,
                                                       'date_deadline': datetime.today(),
                                                       'summary': self.employee_no,
                                                       'create_uid' : data.id,
                                                       'user_id': data.id,
                                                       'res_id': self.id,
                                                       'res_model_id': res_model_id,
                                                       'note': message,
                                                       }])

    @api.depends('new_basic_salary', 'new_basic_allowance')
    def _compute_revised_amount(self):
        for rec in self:
            if not rec.new_basic_salary:
                rec.revised_wage = rec.old_wage#rec.new_basic_salary + rec.new_basic_allowance
            else:
                rec.revised_wage = rec.new_basic_salary + rec.new_basic_allowance 

    # Constraints and onchanges
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """
            Onchange used to get the values from contract
            and reflect on increment form
        """
        if self.employee_id:
            self.old_basic_salary = self.employee_id.contract_id.basic_salary
            self.old_basic_allowance = self.employee_id.contract_id.basic_allowance
            self.old_extra_allowance = self.employee_id.contract_id.extra_allowance
            self.old_total_deduction = self.employee_id.contract_id.net_deduction
            self.contract_id = self.employee_id.contract_id.id
            self.start_date = self.employee_id.contract_id.date_start
            self.first_contract = self.employee_id.contract_id.first_contract_date
            self.date_of_join = self.employee_id.joining_date
            # self.new_basic_salary = self.employee_id.contract_id.basic_salary
            self.old_monthly_advantages_ids = [(5, 0, 0)]
            self.new_monthly_advantages_ids = [(5, 0, 0)]
            for data in self.employee_id.contract_id.allowances_ids:
                self.env['old.monthly.advantages'].create({
                    'old_allowance_id': data.allowance_id.id,
                    'old_category': data.category,
                    'old_type': data.type,
                    'old_rate': data.rate,
                    'old_amount': data.amount,
                    'old_emp_increment_id': self.id,
                })
                self.env['new.monthly.advantages'].create({
                    'allowance_id': data.allowance_id.id,
                    'category': data.category,
                    'type': data.type,
                    'emp_increment_id': self.id,
                    'rate': data.rate,
                    'old_rate': data.rate,
                    'amount': data.amount,
                    'final_amount' : data.amount
                })

    @api.onchange('new_monthly_advantages_ids')
    def _onchange_new_monthly_advantages_ids(self):
        """
            Onchange used to get the total of amount from new increment lines
        """
        if self.new_monthly_advantages_ids:
            total = 0
            for data in self.new_monthly_advantages_ids:
                total += data.final_amount
            self.new_basic_allowance = total

    @api.depends('addition_type','addition_value','percentage','old_basic_salary')
    def _compute_new_salary(self):
        if self.addition_type == 'amount':
            self.new_basic_salary = self.old_basic_salary + self.addition_value
        elif self.addition_type == 'percentage':
            if self.old_basic_salary:
                revised_amount = (self.old_basic_salary * self.percentage) / 100
                self.new_basic_salary = self.old_basic_salary + revised_amount

    # @api.onchange('addition_type', 'percentage', 'addition_value', 'old_basic_salary')
    # def calculate_new_basic_salary(self):
    #     """
    #     Caluclte new basic salary on the bases on type
    #     """
    #     if self.addition_type == 'amount':
    #         if self.old_basic_salary and self.addition_value:
    #             self.new_basic_salary = self.old_basic_salary + self.addition_value
    #     elif self.addition_type == 'percentage':
    #         if self.old_basic_salary and self.percentage:
    #             revised_amount = (self.old_basic_salary * self.percentage) / 100
    #             self.new_basic_salary = self.old_basic_salary + revised_amount

    # Action methods
    def update_increment_on_contract(self):
        records = self.env['emp.increment'].search(
            [('effective_date', '<=', date.today()), ('state', '=', 'approve')])
        if records:
            for rec in records:
                rec.contract_id.update({
                    'basic_salary': rec.new_basic_salary
                })
                total_months = (fields.date.today().year - rec.employee_id.hire_date.year) * 12 + (
                            fields.date.today().month - rec.employee_id.hire_date.month)
                before_increment = rec.before_increment(total_months)
                for advantage in rec.new_monthly_advantages_ids:
                    for allowances in rec.contract_id.allowances_ids:
                        if advantage.allowance_id.id == allowances.allowance_id.id:
                            if allowances.type == 'Amount':
                                allowances.update({
                                    'rate': advantage.rate,
                                    'amount': advantage.final_amount,
                                })
                            else:
                                allowances.update({
                                    'amount': advantage.final_amount,
                                })
                rec.contract_id.compute_wage()
                after_increment = rec.check_allocation_type(total_months, before_increment)
                rec.update({
                    'state': 'done'
                })

    #
    # after five year genrate provision Entry
    #
    #

    def five_year_provision_entry(self):
        employees = self.env['hr.employee'].search([('five_year_provision', '=', False)])
        for emp in employees:
            if emp.hire_date:
                difference_in_years = relativedelta(fields.Date.today(), emp.hire_date).years
                if relativedelta(fields.Date.today(), emp.hire_date).years == 5 and relativedelta(fields.Date.today(),
                                                                                                  emp.hire_date).months == 0 and relativedelta(
                        fields.Date.today(), emp.hire_date).days == 0:
                    total_months = (fields.date.today().year - emp.hire_date.year) * 12 + (
                            fields.date.today().month - emp.hire_date.month)
                    before_five_year = self.before_five_year_provision(emp, total_months)
                    after_five_year = self.after_five_year_provision(emp, total_months, before_five_year)
                    emp.update({
                        'five_year_provision': True
                    })

    def before_five_year_provision(self, emp, months):
        if emp:
            if not emp.hire_date:
                raise UserError(_('Please Configure Hire Date in Employee : %s') % (self.employee_id.name))
            # EOS
            eos_config_id = self.env['provision.configuration'].search(
                [('type', '=', 'EOS'), ('struct_id', '=', emp.contract_id.struct_id.id)],
                limit=1)
            if eos_config_id and eos_config_id.journal_id and eos_config_id.debit_account_id and eos_config_id.credit_account_id:
                todaydate = fields.date.today()
                last_date = calendar._monthlen(int(todaydate.year), int(todaydate.month) - 1)
                provision = self._type_eos(emp, eos_config_id,
                                           datetime.date(int(todaydate.year), int(todaydate.month) - 1, 1),
                                           datetime.date(int(todaydate.year), int(todaydate.month) - 1, last_date),
                                           emp.contract_id.wage)

                name = emp.name + ' - ' + eos_config_id.name
                provision['data'][0]['amount'] = provision['data'][0]['amount'] * int(months)
                data_eos = {
                    'provision_amount': provision['data'][0]['amount'],
                }

            data = {
                'eos_data': data_eos,
            }
            return data

    def after_five_year_provision(self, emp, months, previous_data):
        if emp:
            if not emp.hire_date:
                raise UserError(_('Please Configure Hire Date in Employee : %s') % (emp.name))
            # EOS
            eos_config_id = self.env['provision.configuration'].search(
                [('type', '=', 'EOS'), ('struct_id', '=', emp.contract_id.struct_id.id)],
                limit=1)
            if eos_config_id and eos_config_id.journal_id and eos_config_id.debit_account_id and eos_config_id.credit_account_id:
                todaydate = fields.date.today()
                last_date = calendar._monthlen(int(todaydate.year), int(todaydate.month) + 1)
                provision = self._type_eos(emp, eos_config_id,
                                           datetime.date(int(todaydate.year), int(todaydate.month) + 1, 1),
                                           datetime.date(int(todaydate.year), int(todaydate.month) + 1, last_date),
                                           emp.contract_id.wage)
                name = emp.name + ' - ' + eos_config_id.name

                previous_provision = 0.0
                if 'eos_data' in previous_data:
                    previous_provision = previous_data['eos_data']['provision_amount']
                provision['data'][0]['amount'] = (provision['data'][0]['amount'] * int(months)) - previous_provision
                ref = ' Adjustment for complete 5 year'
                self._create_provision(provision, emp, eos_config_id, name, ref)

    #
    # end after five year genrate provision Entry
    #
    #
    # for provision on increment
    def _get_end_date(self, start_date):
        """return the end date of provision"""
        return start_date
        # if isinstance(start_date,date):
        #     month = self.date_from.strftime("%m")
        #     year = self.date_from.strftime("%Y")
        #     last_day = calendar.monthrange(int(year),int(month))[1]
        #     return datetime.datetime(int(year),int(month),last_day).date()
        # else:
        #     return False

    def _type_eos(self, employee_id, config_id, start_date, end_date, amount):
        """return calculation for es provision"""
        vals = {'data': []}
        hire_date = employee_id.hire_date
        LessCond = config_id.eos_config_line.filtered(lambda l: l.sign == 'l')
        GreatCond = config_id.eos_config_line.filtered(lambda l: l.sign == 'g')
        less_year = hire_date + relativedelta(years=LessCond.year)
        if start_date < less_year and end_date >= less_year:
            f_cond_amount = (amount / (2 if LessCond.salary == 'half' else 1))
            s_cond_amount = (amount / (1 if GreatCond.salary == 'full' else 2))
            f_monthly = f_cond_amount / 12
            s_monthly = s_cond_amount / 12
            post_date = start_date
            break_month = less_year.strftime("%m")
            while post_date < end_date:
                if int(post_date.strftime("%m")) == int(break_month):
                    break_date = less_year.strftime("%d")
                    break_year = less_year.strftime("%Y")
                    last_day_of_month = calendar.monthrange(int(break_year), int(break_month))[1]
                    break_daily_amount = (f_monthly / last_day_of_month)
                    new_daily_amount = (s_monthly / last_day_of_month)
                    data_f = {
                        'start_date': post_date,
                        'amount': (break_daily_amount * (int(break_date) - 1)),
                        'end_date': self._get_end_date(post_date)
                    }
                    vals['data'].append(data_f)
                    data_s = {
                        'start_date': less_year,
                        'amount': (new_daily_amount * ((last_day_of_month - int(break_date)) + 1)),
                        'end_date': self._get_end_date(less_year)
                    }
                    vals['data'].append(data_s)
                elif post_date < less_year:
                    data = {
                        'start_date': post_date,
                        'amount': f_monthly,
                        'end_date': self._get_end_date(post_date)
                    }
                    vals['data'].append(data)
                elif post_date > less_year:
                    data = {
                        'start_date': post_date,
                        'amount': s_monthly,
                        'end_date': self._get_end_date(post_date)
                    }
                    vals['data'].append(data)
                post_date += relativedelta(months=1)
            vals.update({'post_date': start_date})
        elif start_date >= less_year:
            monthly_amount = (amount / (1 if GreatCond.salary == 'full' else 2)) / 12
            post_date = start_date
            while post_date < end_date:
                data = {
                    'start_date': post_date,
                    'amount': monthly_amount,
                    'end_date': self._get_end_date(post_date)
                }
                vals['data'].append(data)
                post_date += relativedelta(months=1)
            vals.update({'post_date': start_date})
        else:
            monthly_amount = (amount / (2 if LessCond.salary == 'half' else 1)) / 12
            post_date = start_date
            while post_date < end_date:
                data = {
                    'start_date': post_date,
                    'amount': monthly_amount,
                    'end_date': self._get_end_date(post_date)
                }
                vals['data'].append(data)
                post_date += relativedelta(months=1)
            vals.update({'post_date': start_date})
        return vals

    # Type Vacation
    def _type_vacation(self, employee_id, config_id, start_date, end_date, amount):
        """return vacation values for provision """
        vals = {'data': []}
        if employee_id.hire_date <= start_date:
            monthly_amount = (amount / 30) * (employee_id.contract_id.level.annual / 12)
            post_date = start_date
            while post_date < end_date:
                data = {
                    'start_date': post_date,
                    'amount': monthly_amount,
                    'end_date': self._get_end_date(post_date)
                }
                vals['data'].append(data)
                post_date += relativedelta(months=1)
            vals.update({'post_date': start_date})
        else:
            working_days = (int(end_date.day) - int(employee_id.hire_date.day)) + 1
            monthly_amount = (amount / 30) * (((employee_id.contract_id.level.annual / 12) / 30) * working_days)
            post_date = start_date
            while post_date < end_date:
                data = {
                    'start_date': post_date,
                    'amount': monthly_amount,
                    'end_date': self._get_end_date(post_date)
                }
                vals['data'].append(data)
                post_date += relativedelta(months=1)
            vals.update({'post_date': end_date})
        return vals

    # Create Provision
    def _create_provision(self, datas, employee_id, config_id, name,adjustment=False):
        """ create provision"""
        if isinstance(datas, dict):
            provision_id = self.env['account.provision'].search(
                [('employee_id', '=', employee_id.id), ('provision_type_id', '=', config_id.id),
                 ('state', '=', 'running')], limit=1)
            lineObj = self.env['account.provision.line']
            analytic_id = self.env['account.analytic.account'].search(
                [('id', '=', employee_id.contract_id.analytic_account_id.id)], limit=1)
            if not provision_id:
                provision_id = self.env['account.provision'].create({
                    'name': name,
                    'provision_type_id': config_id.id,
                    'employee_id': employee_id.id,
                    'cost_center': analytic_id.id if analytic_id else False,
                    'post_date': datas['post_date'],
                    'state': 'running'
                })
            provision_id.update({
                'cost_center': employee_id.contract_id.analytic_account_id.id
            })
            for data in datas['data']:
                line_id = lineObj.create({
                    'date': data['start_date'],
                    'value': data['amount'],
                    'end_date': data.get('end_date'),
                    'provision_id': provision_id.id,
                })
                line_id.create_move(adjustment=adjustment)

    def last_day_of_month(any_day):
        # this will never fail
        # get close to the end of the month for any day, and add 4 days 'over'
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
        # subtract the number of remaining 'overage' days to get last day of current month, or said programattically said, the previous day of the first of next month
        return next_month - datetime.timedelta(days=next_month.day)

    # Check Allocation type and Create provision
    def check_allocation_type(self, months, previous_data):
        if self.employee_id:
            if not self.employee_id.hire_date:
                raise UserError(_('Please Configure Hire Date in Employee : %s') % (self.employee_id.name))
            # EOS
            eos_config_id = self.env['provision.configuration'].search(
                [('type', '=', 'EOS'), ('struct_id', '=', self.contract_id.struct_id.id)],
                limit=1)
            if eos_config_id and eos_config_id.journal_id and eos_config_id.debit_account_id and eos_config_id.credit_account_id:
                todaydate = fields.date.today()
                last_date = calendar._monthlen(int(todaydate.year), int(todaydate.month))
                provision = self._type_eos(self.employee_id, eos_config_id,
                                           datetime.date(int(todaydate.year), int(todaydate.month), 1),
                                           datetime.date(int(todaydate.year), int(todaydate.month), last_date),
                                           self.contract_id.wage)
                name = self.employee_id.name + ' - ' + eos_config_id.name
                previous_provision = 0.0
                if 'eos_data' in previous_data:
                    previous_provision = previous_data['eos_data']['provision_amount']
                provision['data'][0]['amount'] = (provision['data'][0]['amount'] * int(months)) - previous_provision
                ref = ' Adjustment for Increment'
                self._create_provision(provision, self.employee_id, eos_config_id, name,ref)

            # Vaction
            vac_config_id = self.env['provision.configuration'].search(
                [('type', '=', 'Vacation'), ('struct_id', '=', self.contract_id.struct_id.id)], limit=1)
            if vac_config_id and vac_config_id.journal_id and vac_config_id.debit_account_id and vac_config_id.credit_account_id:
                todaydate = fields.date.today()
                last_date = calendar._monthlen(int(todaydate.year), int(todaydate.month))
                provision = self._type_vacation(self.employee_id, vac_config_id, datetime.date(int(todaydate.year),int(todaydate.month),1), datetime.date(int(todaydate.year),int(todaydate.month),last_date), self.contract_id.wage)
                name = self.employee_id.name + ' - ' + vac_config_id.name
                vacc_previous_provision = 0.0
                if 'vec_data' in previous_data:
                    vacc_previous_provision = previous_data['vec_data']['provision_amount']
                provision['data'][0]['amount'] = (provision['data'][0]['amount'] * int(months)) - vacc_previous_provision
                ref = ' Adjustment for Increment'
                self._create_provision(provision, self.employee_id, vac_config_id, name,ref)

    def before_increment(self, months):
        data = {}
        if self.employee_id:
            if not self.employee_id.hire_date:
                raise UserError(_('Please Configure Hire Date in Employee : %s') % (self.employee_id.name))
            # EOS
            eos_config_id = self.env['provision.configuration'].search(
                [('type', '=', 'EOS'), ('struct_id', '=', self.contract_id.struct_id.id)],
                limit=1)
            if eos_config_id and eos_config_id.journal_id and eos_config_id.debit_account_id and eos_config_id.credit_account_id:
                todaydate = fields.date.today()
                # last_date = calendar._monthlen(int(todaydate.year), int(todaydate.month))
                last_date = calendar.monthrange(todaydate.year,todaydate.month)[1]
                provision = self._type_eos(self.employee_id, eos_config_id,
                                           datetime.date(todaydate.year, todaydate.month, 1),
                                           datetime.date(todaydate.year, todaydate.month, last_date),
                                           self.contract_id.wage)
                name = self.employee_id.name + ' - ' + eos_config_id.name

                provision['data'][0]['amount'] = provision['data'][0]['amount'] * int(months)
                data_eos = {
                    'provision_amount': provision['data'][0]['amount'],
                }

            # Vaction
            vac_config_id = self.env['provision.configuration'].search(
                [('type', '=', 'Vacation'),
                 ('struct_id', '=', self.contract_id.struct_id.id)], limit=1)
            if vac_config_id and vac_config_id.journal_id and vac_config_id.debit_account_id and vac_config_id.credit_account_id:
                todaydate = fields.date.today()
                last_date = calendar._monthlen(int(todaydate.year), int(todaydate.month))
                provision = self._type_vacation(self.employee_id, vac_config_id,
                                                datetime.date(int(todaydate.year), int(todaydate.month), 1),
                                                datetime.date(int(todaydate.year), int(todaydate.month), last_date),
                                                self.contract_id.wage)
                name = self.employee_id.name + ' - ' + vac_config_id.name
                provision['data'][0]['amount'] = provision['data'][0]['amount'] * int(months)

                data_vec = {
                    'provision_amount': provision['data'][0]['amount']
                }
                data = {
                    'eos_data': data_eos,
                    'vec_data': data_vec,
                }
            return data

    # end provision
    def action_approve(self):
        for data in self.activity_ids:
            data.action_done()        
        self.state = 'approve'

class OldMonthlyAdvantages(models.Model):
    # Private Attribute
    _name = 'old.monthly.advantages'
    _description = 'Old Monthly Advantages'

    # Declaring Fields
    old_emp_increment_id = fields.Many2one('emp.increment', string='Old Emp Increment')
    old_allowance_id = fields.Many2one('hr.allowance', string='Allowance')
    old_category = fields.Selection([('basic', 'Basic'),
                                     ('allowance1', 'Allowance 1'),
                                     ('allowance2', 'Other Allowance 2')], string='Category')
    old_type = fields.Selection([('Amount', 'Amount'),
                                 ('Percentage', 'Percentage')], string='Type')
    old_rate = fields.Float('Rate/Amount')
    old_amount = fields.Float(string="Amount")


class NewMonthlyAdvantages(models.Model):
    # Private Attribute
    _name = 'new.monthly.advantages'
    _description = 'New Monthly Advantages'

    # Declaring Fields
    emp_increment_id = fields.Many2one('emp.increment', string='New Emp Increment')
    allowance_id = fields.Many2one('hr.allowance', string='Allowance')
    category = fields.Selection([('basic', 'Basic'),
                                 ('allowance1', 'Allowance 1'),
                                 ('allowance2', 'Other Allowance 2')], string='Category')
    type = fields.Selection([('Amount', 'Amount'),
                             ('Percentage', 'Percentage')], string='Type', default='Amount')
    old_rate = fields.Float(string="Rate")
    rate = fields.Float('Rate/Amount')
    amount = fields.Float(string="Update Amount", store=True)
    final_amount = fields.Float(string="Final Amount")

    # #for updating data based on parent class changes
    # @api.depends('emp_increment_id.addition_type','emp_increment_id.percentage')
    # def _update_amount(self):
    #     for data in self:
    #         # if data.emp_increment_id.percentage == 0:
    #         #     data.amount = data.old_rate
    #         #     data.rate = data.old_rate
    #             # //and data.emp_increment_id.percentage
    #         if data.emp_increment_id.addition_type == 'percentage'  and data.type == 'Percentage':
    #             if data.old_rate:
    #                 revised_amount = (data.old_rate * data.emp_increment_id.percentage) / 100
    #                 data.amount = data.old_rate + revised_amount
    #                 data.rate = data.old_rate + revised_amount
    #             else:
    #                 data.amount = data.old_rate
    #                 data.rate = data.old_rate
    #         else:
    #             data.amount = data.old_rate
    #             data.rate = data.old_rate

    # compute and search fields, in the same order of fields declaration
    @api.onchange('type', 'rate', 'emp_increment_id')
    def get_amount(self):
        """
        it calc total amount according to formula
        """
        final_amount = old_amount =  0
        for rec in self:
            if rec.type == 'Amount':
                if rec.emp_increment_id.old_monthly_advantages_ids:
                    for i in rec.emp_increment_id.old_monthly_advantages_ids:
                        if rec.allowance_id.id == i.old_allowance_id.id:
                            rec.amount = rec.rate
                            rec.final_amount = i.old_amount + rec.amount
                            if rec.allowance_id.min_fix_amount or rec.allowance_id.max_fix_amount:
                                if rec.allowance_id.min_fix_amount and rec.amount < rec.allowance_id.min_fix_amount:
                                    rec.amount = rec.allowance_id.min_fix_amount
                                elif rec.allowance_id.max_fix_amount and rec.amount > rec.allowance_id.max_fix_amount:
                                    rec.amount = rec.allowance_id.max_fix_amount
                                    # rec.final_amount  = rec.amount + i.old_amount
                                rec.final_amount  = rec.amount + i.old_amount
                                if rec.final_amount < rec.allowance_id.min_fix_amount:
                                    rec.final_amount = rec.allowance_id.min_fix_amount
                                elif rec.amount > rec.allowance_id.max_fix_amount:
                                    rec.final_amount = rec.allowance_id.max_fix_amount
            elif rec.type == 'Percentage':
                if rec.emp_increment_id:
                    for i in rec.emp_increment_id.old_monthly_advantages_ids:
                        if rec.allowance_id.id == i.old_allowance_id.id:
                            # rec.amount = i.old_amount + (i.old_amount * rec.rate / 100)
                            # old_amount = i.old_amount
                            increment_amount = (i.old_amount * (rec.rate / 100))
                            rec.amount = (increment_amount + i.old_amount)
                            rec.final_amount = rec.amount
                            if rec.allowance_id.min_fix_amount or rec.allowance_id.max_fix_amount:
                                if rec.allowance_id.min_fix_amount and rec.amount < rec.allowance_id.min_fix_amount:
                                    rec.amount = rec.allowance_id.min_fix_amount
                                    # rec.final_amount = rec.amount + i.old_amount
                                elif rec.allowance_id.max_fix_amount and rec.amount > rec.allowance_id.max_fix_amount:
                                    rec.amount = rec.allowance_id.max_fix_amount
                                    # rec.final_amount = rec.amount + i.old_amount
                                rec.final_amount = rec.amount + i.old_amount
                                
                                if rec.final_amount < rec.allowance_id.min_fix_amount:
                                    rec.final_amount = rec.allowance_id.min_fix_amount
                                elif rec.final_amount > rec.allowance_id.max_fix_amount:
                                    rec.final_amount = rec.allowance_id.max_fix_amount
                        # else:
                        #     # rec.amount = i.old_amount + (i.old_amount * rec.rate / 100)
                        #     rec.amount = (rec.emp_increment_id.new_basic_salary * (rec.rate / 100))
                        #     rec.final_amount = rec.amount + i.old_amount
            else:
                rec.amount = 0.0
