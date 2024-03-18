# -*- coding: utf-8 -*-

from collections import defaultdict
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from datetime import timedelta
from collections import namedtuple
from calendar import monthrange
from datetime import datetime
from datetime import datetime, date, time
import calendar
import pytz

Range = namedtuple('Range', ['start', 'end'])


class HrPayslip(models.Model):
    # Private attributes
    _inherit = 'hr.payslip'

    # Fields declaration
    unpaid_leaves = fields.Integer('Unpaid Leaves days')
    over_time = fields.Float('Total Over Time')
    actually_over_time = fields.Float('Actually Over Time')
    per_day_cost = fields.Float("Per Day Cost")
    per_hour_cost = fields.Float("Per Hour Cost")
    basic_salary_cost = fields.Float("Basis Salary (Per Hour Cost)")
    computed_salary = fields.Float(store=True)
    state = fields.Selection(selection_add=[('hr', 'Hr Approve'),('verify', 'Waiting')])
    input_line_ids = fields.One2many('hr.payslip.input', 'payslip_id', string='Payslip Inputs',
                                     readonly=True,
                                     states={'draft': [('readonly', False)],'hr': [('readonly', False)], 'verify': [('readonly', False)]})
    salary_days_count = fields.Integer()
    overtime_amount = fields.Float(string="Overtime Amount", compute="_compute_overtime_amount", store=True)

    @api.depends('state', 'actually_over_time')
    def _compute_overtime_amount(self):
        for data in self:
            if data.actually_over_time:
                data.overtime_amount = data.actually_over_time * data.per_hour_cost
            else:
                data.overtime_amount = 0

    # Constraints and onchanges
    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        """
        this function get all time off in given time interval and calculate unpaid time
        """
        for rec in self:
            unpaid_leaves = self.env['hr.leave'].search(
                [('employee_id', '=', rec.employee_id.id), ('holiday_status_id.unpaid', '=', True), ('state', '=', 'validate')])
            check_start_month = rec.date_from.month
            check_end_month = rec.date_to.month
            days = 0
            holiday = 0
            for leaves in unpaid_leaves:
                if (leaves.request_date_from.month == check_start_month or leaves.request_date_to.month == check_start_month) or (leaves.request_date_from.month == check_end_month or leaves.request_date_to.month == check_end_month) or (leaves.request_date_from < rec.date_from and leaves.request_date_to > rec.date_to):
                    r1 = Range(start=rec.date_from, end=rec.date_to)
                    r2 = Range(start=leaves.request_date_from, end=leaves.request_date_to)
                    latest_start = max(r1.start, r2.start)
                    earliest_end = min(r1.end, r2.end)
                    delta = (earliest_end - latest_start).days + 1
                    overlap = max(0, delta)
                    day_count = (leaves.request_date_to - leaves.request_date_from).days + 1
                    for i in (leaves.request_date_from + timedelta(n) for n in range(day_count)):
                        day = int(i.strftime("%w")) - 1
                        if day == -1:
                            day = 6
                        day = str(day)
                        if not leaves.holiday_status_id.include_holidays:
                            for emp_day in rec.employee_id.resource_calendar_id.attendance_ids:
                                if emp_day.dayofweek == day and emp_day.day_period == 'morning':
                                    if i <= rec.date_to:
                                        holiday = holiday + 1
                        else:
                            holiday = holiday + 1
                    days = days + overlap
            rec.unpaid_leaves = days
            #             calculate over time
            # total_over_time = actually_over_time = 0
            # for i in self.env['over.time.line'].search([('employee_id', '=', rec.employee_id.id),
            #                                             ('overtime_id.state', '=', 'approve'),
            #                                             ('overtime_id.month','=',str(rec.date_to.month)),
            #                                             ('overtime_id.year','=',str(rec.date_to.year))]):
            #     total_over_time = total_over_time + i.approved_overtime
            #     if i.overtime_id.over_time_type_id.multiple_by:
            #         actually_over_time += i.approved_overtime * i.overtime_id.over_time_type_id.multiple_by
            #     else:
            #         actually_over_time += i.approved_overtime
            # rec.over_time = total_over_time
            # rec.actually_over_time = actually_over_time
            #   Per day cost
            if rec.contract_id.wage:
                rec.per_day_cost = rec.contract_id.wage / 30
            #   Per hour cost
                rec.per_hour_cost = rec.contract_id.wage / 30 / 8
                if rec.contract_id.basic_salary :
                    rec.basic_salary_cost = rec.contract_id.basic_salary / 30 / 8
            if rec.contract_id and rec.contract_id.wage:
                if rec.contract_id.joining_date:
                    if rec.contract_id.joining_date <= rec.date_to:
                        if rec.contract_id.joining_date.month == rec.date_from.month or rec.contract_id.joining_date.month == rec.date_to.month:
                            per_day_wage = rec.contract_id.wage / 30
                            working_days = rec.date_to - rec.contract_id.joining_date
                            rec.computed_salary = working_days.days * per_day_wage
                        elif rec.contract_id.joining_date.month < rec.date_from.month or rec.contract_id.joining_date.month < rec.date_to.month:
                            rec.computed_salary = rec.contract_id.wage
                        else:
                            rec.computed_salary = 0

                    #     important but commented
                    # if rec.contract_id.joining_date.month == rec.date_from.month or rec.contract_id.joining_date.month == rec.date_to.month:
                    #     per_day_wage = rec.contract_id.wage / 30
                    #     working_days = rec.date_to - rec.contract_id.joining_date
                    #     rec.salary_days_count = int(working_days.days) + 1
                    #     rec.computed_salary = (int(working_days.days) + 1) * per_day_wage
                    # elif rec.contract_id.joining_date.month < rec.date_from.month or rec.contract_id.joining_date.month < rec.date_to.month:
                    #     working_days = rec.date_to - rec.date_from
                    #     rec.salary_days_count = int(working_days.days) + 1
                    #     rec.computed_salary = rec.contract_id.wage
                    # else:
                    #     rec.computed_salary = 0

                    #     end
                    else:
                        raise UserError(
                            _('You try to Made payroll before joining'),
                        )

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee_info(self):
        """
        this function get contract and salary structure of employee
        """
        if self.employee_id and self.employee_id.contract_id:
            self.contract_id = self.employee_id.contract_id.id
        else:
            self.contract_id = False
        if self.employee_id and self.employee_id.contract_id and self.employee_id.contract_id.structure_type_id.default_struct_id:
            self.struct_id = self.employee_id.contract_id.structure_type_id.default_struct_id
        else:
            self.struct_id = False

    # CRUD methods (and name_get, name_search, ...) overrides
    @api.model
    def create(self, values):
        """
        validation on contract state
        """
        res = super(HrPayslip, self).create(values)
        if not res.sudo().employee_id.contract_id or res.sudo().employee_id.contract_id.state != 'open':
            raise UserError(
                _('The Contract for %s not in running state' %
                  res.sudo().employee_id.name),
            )
        res._check_work_entry()
        return res

    #make method to check work entry validation on it too..
    def _check_work_entry(self):
        for data in self:
            work_entries = self.env['hr.work.entry'].search([
                ('date_start', '>=', data.date_from),
                ('date_stop', '<=', data.date_to),
                ('employee_id', '=', data.employee_id.id)])
            self._check_undefined_slots(work_entries, data.date_from,data.date_to)

    #make method to check validation with single payslip
    def _check_undefined_slots(self, work_entries, date_from,date_to):
        """
        Check if a time slot in the contract's calendar is not covered by a work entry
        """
        work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])
        for work_entry in work_entries:
            work_entries_by_contract[work_entry.contract_id] |= work_entry

        for contract, work_entries in work_entries_by_contract.items():
            calendar_start = pytz.utc.localize(datetime.combine(max(contract.date_start, date_from), time.min))
            calendar_end = pytz.utc.localize(datetime.combine(min(contract.date_end or date.max, date_to), time.max))
            outside = contract.resource_calendar_id._attendance_intervals_batch(calendar_start, calendar_end)[False] - work_entries._to_intervals()
            if outside:
                time_intervals_str = "\n - ".join(['', *["%s -> %s" % (s[0], s[1]) for s in outside._items]])
                raise UserError(_("Some part of %s's calendar is not covered by any work entry. Please complete the schedule. Time intervals to look for:%s") % (contract.employee_id.name, time_intervals_str))

    # def write(self, vals):
    #     """
    #     validation on contract state
    #     """
    #     res = super(HrPayslip, self).write(vals)
    #     if vals.get('employee_id'):
    #         for payslip in self:
    #             if not payslip.sudo().employee_id.contract_id or payslip.sudo().employee_id.contract_id.state != 'open':
    #                 raise UserError(
    #                     _('The Contract for %s not in running state' %
    #                       payslip.sudo().employee_id.name),
    #                 )
    #     return res

    def unlink(self):
        """
        this ristric the delete of record
        """
        for rec in self:
            if not self.env.user.has_group('base.group_system'):
                raise UserError(_("You have not access to delete this record."))
            else:
                return super(HrPayslip,self).unlink()

    # Action methods
    def hr_approved(self):
        """
        this approved the state
        :return:
        """
        self.state = 'verify'

    def compute_sheet(self):
        """
        this is enhancement of payslip compute sheet method
        """
        for rec in self:
            if rec.state not in ['draft', 'verify']:
                old_state = rec.state
                rec.state = 'draft'
                res = super(HrPayslip, self).compute_sheet()
                rec.state = old_state
            else:
                res = super(HrPayslip, self).compute_sheet()
            return res

    # Business methods
    def calculate_deduction(self,employee_id,date_from,date_to,code):
        """
        calculate deduction
        """
        deductions = self.env['payroll.deduction'].search([('state','=','approve'),('employee_id','=',employee_id),('date','>=',date_from),('date','<=',date_to),('deduction_type.short_code','=',code)])
        tot_deduction = 0
        if deductions:
            for i in deductions:
                tot_deduction = tot_deduction + i.deduct_price
        return tot_deduction

    def calculate_allowances(self,employee_id,date_from,date_to,code):
        """
        calculate deduction
        """
        allowances = self.env['payroll.allowance'].search([('state','=','approve'),('employee_id','=',employee_id),('date','>=',date_from),('date','<=',date_to),('allowance_type.short_code','=',code)])
        tot_allowances = 0
        if allowances:
            for i in allowances:
                tot_allowances = tot_allowances + i.allowance_price
        return tot_allowances

    def calculate_contract_allownces(self,employee_id,date_from,date_to,code):
        """
        calculate allownces
        """
        employee = self.env['hr.employee'].search([('id','=', employee_id)])
        if employee and employee.contract_id:
            if date_to >= employee.contract_id.joining_date > date_from:
                days_of_month = calendar.monthrange(date_to.year, date_to.month)[1]
                total = 0
                for line in employee.contract_id.allowances_ids:
                    if line.allowance_id.name == code:
                        total = line.amount
                per_day_value = total / 30
                end_date_of_month = datetime(year=int(date_to.year), month=int(date_to.month), day=int(days_of_month))
                earned_days = end_date_of_month.date() - employee.contract_id.joining_date
                return round(((int(earned_days.days)+1) * per_day_value), 2)
            elif employee.contract_id.joining_date <= date_from:
                total = 0
                for line in employee.contract_id.allowances_ids:
                    if line.allowance_id.name == code:
                        total = line.amount
                return round(total, 2)

    def calculate_basic_salary(self,employee_id,date_from,date_to):
        """calculate Basic Salary"""
        employee = self.env['hr.employee'].search([('id', '=', employee_id)])
        if employee and employee.contract_id:
            if date_to >= employee.contract_id.joining_date > date_from:
                days_of_month = calendar.monthrange(date_to.year, date_to.month)[1]
                per_day_value = employee.contract_id.basic_salary / 30
                end_date_of_month = datetime(year=int(date_to.year), month=int(date_to.month), day=int(days_of_month))
                earned_days = end_date_of_month.date() - employee.contract_id.joining_date
                return round(((int(earned_days.days)+1) * per_day_value), 2)
            elif employee.contract_id.joining_date <= date_from:
                return round(employee.contract_id.basic_salary, 2)

    #disable action button in create draft entry 
    def fields_view_get(self, view_id=None, view_type='tree', toolbar=False,
                        submenu=False):
        res = super(HrPayslip, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if not self._context.get('validate', False):
            create_draft_entry = self.env.ref('hr_payroll.action_hr_payroll_confirm_payroll').id or False
            for button in res.get('toolbar', {}).get('action', []):
                if create_draft_entry and button['id'] == create_draft_entry:
                    res['toolbar']['action'].remove(button)
            return res

        # deductions = self.env['payroll.deduction'].search([('employee_id','=',employee_id),('date','>=',date_from),('date','<=',date_to),('deduction_type.short_code','=',code)])
        # tot_deduction = 0
        # if deductions:
        #     for i in deductions:
        #         tot_deduction = tot_deduction + i.deduct_price
        # return tot_deduction


class HrManagerApprove(models.Model):

    # Private attributes
    _name = 'hr.manager.approve'
    _description = 'Marking payslip hr Manager approve'

    # Action methods
    def mark_manager_approve(self):
        """
        it'll approve the payslip in bulk by hr manager
        """
        selected = self.env['hr.payslip'].browse(self._context.get('active_ids'))
        if selected:
            for one in selected:
                if self.env.user.has_group('hr.group_hr_manager') and one.state == 'hr':
                    one.hr_approved()

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    arbic_name = fields.Char('Arabic Name')