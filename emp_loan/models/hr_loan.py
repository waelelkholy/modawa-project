# -*- coding: utf-8 -*-
import html2text
import json
from odoo import models, fields, api, _, tools
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm
from odoo.exceptions import UserError, ValidationError


class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Loan Request"

    def _compute_loan_amount(self):
        """
        it computes total amount and total paid amount ,balance amount fields
        """
        total_paid = 0.0
        for loan in self:
            for line in loan.loan_lines:
                if line.status == 'done':
                    total_paid += line.amount
            balance_amount = loan.loan_amount - total_paid
            self.total_amount = loan.loan_amount
            self.balance_amount = balance_amount
            self.total_paid_amount = total_paid

    def default_get_journal(self):
        """get default journal"""
        params = self.env['ir.config_parameter'].sudo()
        payment_journal = int(params.get_param('loan_payment_journal', default=False))
        return payment_journal

    name = fields.Char(string="Loan Name", default="/", readonly=True, tracking=True)
    date = fields.Date(string="Date", default=fields.Date.today(), tracking=True)
    requseter_id = fields.Many2one('res.users', string="Requester", default=lambda self: self.env.user, readonly=True,
                                   tracking=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, tracking=True)
    employee_id_domain = fields.Char(compute="_compute_employee_domain", readonly=True, store=False)
    department_id = fields.Many2one(related='employee_id.department_id', string="Department", readonly=True,
                                    tracking=True)
    loan_lines = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", index=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True,
                                 default=lambda self: self.env.company,
                                 states={'draft': [('readonly', False)]}, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    job_id = fields.Many2one(related='employee_id.job_id', string="Job Position", readonly=True,
                             tracking=True)
    loan_amount = fields.Float(string="Loan Amount", required=True, tracking=True)
    total_amount = fields.Float(string="Total Amount", readonly=True, compute='_compute_loan_amount')
    balance_amount = fields.Float(string="Balance Amount", compute='_compute_loan_amount')
    total_paid_amount = fields.Float(string="Total Paid Amount", compute='_compute_loan_amount')
    loan_type_id = fields.Many2one('loan.type', string="Loan Type", copy=False, tracking=True)
    payment_date = fields.Date(string="Installment Date", required=True, default=fields.Date.today(),
                               tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_submit', 'Submit'),
        ('in_process', 'HR Manager'),
        ('ceo', 'CEO'),
        ('approve', 'Approved'),
        ('paid', 'Paid'),
        ('posted', 'Posted'),
        ('reapply', 'Re-Apply'),
        ('cancelled', 'Cancelled'),
        ('hold', 'Hold'),
        ('rejected', 'Rejected')
    ], string="State", default='draft', tracking=True, copy=False)

    installment_type = fields.Selection([
        ('installment_amount', 'Installment Amount'),
        ('installment_no', 'Installment No.'),
    ], string="Payment Type", default='installment_amount', tracking=True, copy=False)
    installment = fields.Integer(string="No Of Installments", default=1)
    installment_amount = fields.Float(string="Installment Amount",
                                      help="this amount deducted from payslip when this payton code is embend in salary rule \n result = -payslip.loan_amount")
    desciption = fields.Text(string="Description", required=True, copy=False)
    payment_id = fields.Many2one(comodel_name="account.payment", string="Payment", copy=False, )
    payment_ids = fields.Many2many(comodel_name="account.payment", string="Loan Cash Payment", copy=False)
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", default=lambda self: self.default_get_journal(), copy=False)
    check_login_user = fields.Boolean(compute="_check_login_user",default=False)
    employee_no = fields.Char('Employee No')
    salary = fields.Float()
    edit_in_process = fields.Boolean(compute="compute_edit_in_process")
    direct_manager = fields.Boolean(compute="check_direct_manager")
    cancel_reason = fields.Char(string="Canecl/Reject Reason", tracking=True)

    #for make validation when select employee on loan module
    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for data in self:
            if data.employee_id:
                if not data.sudo().employee_id.contract_id or data.sudo().employee_id.contract_id.state != 'open':
                    raise UserError(
                        _('This Employee Contract not in running state'),
                    )

    #get domain for employee fields
    @api.depends('requseter_id')
    def _compute_employee_domain(self):
        for data in self:
            if self.env.user.has_group('emp_loan.loan_ceo') or self.env.user.has_group('emp_loan.loan_emp_manager'):
                data.employee_id_domain = json.dumps([])
            else:
                data.employee_id_domain = json.dumps([('user_id', '=', self.env.user.id)])

    #constrains for if requester employee try to create for other 
    @api.constrains('employee_id')
    def constrains_employee_id(self):
        for data in self:
            if self.env.user.has_group('emp_loan.loan_hr') and not self.env.user.has_group('emp_loan.loan_emp_manager'):
                if self.requseter_id.id != self.employee_id.user_id.id:
                    raise UserError(_('You can not Create Loan Request for other Employee...!'))

    #to add restriction about loan installment amount and loan amount
    @api.onchange('loan_amount','installment_amount')
    def onahcange_installment_amount(self):
        for data in self:
            if data.loan_amount and data.installment_amount:
                if data.installment_amount > data.loan_amount:
                    raise UserError(_('Installment Amout Should not Greater than Loan Amount..!'))

    #to add restriction about loan amount request
    @api.constrains('loan_amount','loan_type_id')
    def constrains_loan_amount(self):
        for data in self:
            if data.loan_amount and data.salary and data.loan_type_id:
                # search_loan_configuration_id = self.env['loan.amount.configuration'].search([('loan_type_id','=',data.loan_type_id.id)],limit=1)
                if data.loan_type_id.max_loan_amount_percentage:
                    max_request_amount = ((data.salary * data.loan_type_id.max_loan_amount_percentage) / 100)
                    if data.loan_amount > max_request_amount:
                        raise UserError(_('You can Requst Max %s Percentage of your Salary amount...')%(data.loan_type_id.max_loan_amount_percentage))
            if data.loan_amount and not data.salary:
                raise UserError(_('Please Add Salary First...'))

    #add constainst to not allow user to enter installment amount more than expected..!
    @api.constrains('salary','loan_type_id','installment_amount')
    def check_installment_amount(self):
        if not self.installment_amount:
            raise UserError('Please Add Installment Amoutn')
        amount = 0
        if self.installment_type == 'installment_no':
            amount = self.loan_amount / self.installment
            installment = self.installment
        else:
            amount = self.installment_amount
            installment = self.loan_amount / self.installment_amount
        if self.salary and self.loan_type_id:
            # loan_configuration_id = self.env['loan.amount.configuration'].search([('loan_type_id','=',self.loan_type_id.id)],limit=1)
            if self.loan_type_id.max_deduction > 0:
                max_deduction_amount = ((self.salary * self.loan_type_id.max_deduction) / 100)
                if max_deduction_amount > 0 and max_deduction_amount < amount:
                    raise ValidationError(_("Maximum Deduction %s Should not Exceed with Installment Amount %s...!")%(str(max_deduction_amount),str(amount)))


    @api.depends('employee_id')
    def check_direct_manager(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.parent_id:
                if rec.employee_id.parent_id.user_id.id == self.env.user.id and rec.state == 'in_process':
                    rec.direct_manager = True
                else:
                    rec.direct_manager = False
            else:
                rec.direct_manager = False

    #addinf method to pass again data to hr manager
    def action_return_to_hr(self):
        for data in self:
            data.state = 'in_process'

    #for CEO Approval
    def action_ceo_approval(self):
        for data in self:
            data.state = 'approve'

    @api.depends('state')
    def compute_edit_in_process(self):
        for rec in self:
            if rec.state in ['draft','reapply']:
                rec.edit_in_process = True
            elif rec.state == 'in_process' and self.env.user.has_group('emp_loan.loan_emp_manager'):
                rec.edit_in_process = True
            else:
                rec.edit_in_process = False


    def make_cash_register_payment(self):
        return {
            'name': _('Loan Cash Register Payment'),
            'res_model': 'cash.register.payment',
            'view_mode': 'form',
            'context': {
                'active_model': 'hr.loan',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    @api.depends('state')
    def _check_login_user(self):
        """check current login user """
        for rec in self:
            # if rec.state == 'in_process':
                # if self.env.user.has_group('emp_loan.loan_emp_manager'):
            rec.check_login_user = True

    def make_payment(self):
        """it'll create payment of of loan which give to employee"""
        for rec in self:
            if rec.loan_amount > 0 and not rec.payment_id:
                journal_id = rec.journal_id.id

                if journal_id:
                    payment_method_id = self.env['account.payment.method'].search([('payment_type','=','outbound'), ('name','=','Manual')], limit=1)
                    payment = self.env['account.payment'].create({
                        # 'partner_id': rec.employee_id.address_home_id.id,
                        # 'amount': rec.loan_amount,
                        # 'journal_id': rec.journal_id.id,
                        # 'date': fields.date.today(),
                        # 'payment_type': 'outbound',
                        # 'payment_method_id': payment_method_id.id,
                        # 'partner_type': 'customer',
                        # 'name': rec.name or ' ',

                        'journal_id': rec.journal_id.id,
                        'currency_id': self.currency_id.id,
                        'amount': rec.loan_amount,
                        'date': datetime.today(),
                        'payment_type': 'outbound',
                        'partner_type': 'customer',
                        'partner_id': rec.employee_id.address_home_id.id,
                        'ref': self.name or ' ',
                    })
                    rec.payment_id = payment.id
                    rec.state = 'paid'
                else:
                    raise ValidationError("Loan Payment journal is not define in Configuration")
            else:
                raise ValidationError("Already Paid or No loan Amount")

    def post_payment(self):
        """it post the payment entry"""
        for rec in self:
            if rec.payment_id:
                rec.payment_id.action_post()
                rec.state = 'posted'

    @api.constrains('loan_lines')
    def action_check_loan_lines(self):
        """it check the loan line which include in given time interval"""
        for loan in self:
            total = 0.0
            if loan.state == 'to_submit':
                for line in loan.loan_lines:
                    if line.status in ['pending', 'done']:
                        total += line.amount
                if loan.loan_amount != total:
                    raise UserError(
                        _('Please Check it. loan amount is not more than or less than total of installment.'),
                    )

    def unlink(self):
        for data in self:
            if data.state not in ['draft']:
                raise UserError(
                    _('You can delete only draft status records...'),
                )
        return super(HrLoan, self).unlink()

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('hr.loan.seq')
        res = super(HrLoan, self).create(values)
        if not res.sudo().employee_id.contract_id or res.sudo().employee_id.contract_id.state != 'open':
            raise UserError(
                _('This Employee Contract not in running state'),
            )
        return res

    def action_reject(self):
        self.state = 'rejected'

    def action_reapply(self):
        self.state = 'reapply'

    def set_draft(self):
        self.state = 'draft'

    def send_notification(self, partner_li, notification_template_id):
        ctx = {
            'recipient_users': self.env.user,
        }
        RenderMixin = self.env['mail.render.mixin'].with_context(**ctx)
        body_html = RenderMixin._render_template(notification_template_id.body_html, 'hr.loan', self.ids, post_process=True)[self.id]
        body = tools.html_sanitize(body_html)
        msg_body = html2text.html2text(body)
        msg = self.env['mail.message'].create({
            'subject': self.name,
            'date': fields.datetime.now(),
            'email_from': "'%s'" % self.env.user.name+'<'+str(self.env.user.email)+'>',
            'message_type': 'notification',
            'subtype_id': self.env.ref('mail.mt_comment').id,
            'res_id': self.id,
            'record_name': self.name,
            'body': msg_body,
            'model': 'hr.loan',
        })
        for partner in partner_li:
            self.env['mail.notification'].create({
                'mail_message_id': msg.id,
                'notification_type': 'inbox',
                'res_partner_id': partner.id,
            })

        return True

    def action_submit(self):
        self.state = 'in_process'
        if not self.loan_amount:
            raise UserError(_('Please Add loan amount First...!')) 
        notification_xml_id = 'emp_loan.loan_notification_template'
        notification_template_id = self.env.ref(notification_xml_id, False)
        # self.send_notification([self.employee_id.parent_id.user_id.partner_id], notification_template_id)
        self.compute_installment()

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """it get the department of employee it have"""
        for emp in self:
            emp.department_id = emp.employee_id.department_id.id if emp.employee_id.department_id else False
            # emp.job_id = emp.employee_id.job_idd.id if emp.employee_id.job_idd else False
            emp.employee_no = emp.employee_id.employee_number
            if emp.sudo().employee_id.contract_id:
                emp.salary = emp.sudo().employee_id.contract_id.wage
            # if emp.salary >= 10000:
            #     raise UserError(
            #         _('Loan cannot request for this employee it salary more than or equal to 10000 '),
            #     )

    def action_inprocess(self):
        group = self.env.ref('hr.group_hr_manager')
        notification_xml_id = 'emp_loan.loan_notification_template'
        notification_template_id = self.env.ref(notification_xml_id, False)
        for user in group.users:
            self.send_notification([user.partner_id], notification_template_id)
        for data in self.env['res.users'].search([]):
            if data.has_group('emp_loan.loan_emp_manager'):
                res_model_id = self.env['ir.model'].search(
                    [('name', '=', self._description)]).id
                search_mail_activity_id = self.env['mail.activity'].search([('res_id','=',self.id),('user_id','=',data.id)])
                if not search_mail_activity_id:
                    message = "Please approve the Loan :-" + " " +  str(self.name) + "which is created by :-" + " " +str(self.env.user.name)
                    self.env['mail.activity'].create([{'activity_type_id': 4,
                                                       'date_deadline': datetime.today(),
                                                       'summary': self.name,
                                                       'create_uid' : data.id,
                                                       'user_id': data.id,
                                                       'res_id': self.id,
                                                       'res_model_id': res_model_id,
                                                       'note': message,
                                                       }])
        self.state = 'ceo'

    def action_approved(self):
        if len(self.loan_lines.ids) >= 1:
            for data in self.activity_ids:
                data.action_done()
            self.state = 'approve'
        else:
            raise UserError(
                _('You can not approve...check Installments line'),
            )

    def action_cancel(self):
        self.state = 'cancelled'
        self.loan_lines.unlink()

    def compute_installment(self):
        if not self.installment_amount:
            raise UserError('Please Add Installment Amoutn')
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        for loan in self:
            loan.loan_lines.unlink()
            amount = 0.0
            max_deduction_amount = 0.0
            installment = 1
            TotalLastAmount = 0.0
            date_start = datetime.strptime(str(loan.payment_date), '%Y-%m-%d')
            if loan.installment_type == 'installment_no':
                amount = loan.loan_amount / loan.installment
                installment = loan.installment
            else:
                amount = loan.installment_amount
                installment = loan.loan_amount / loan.installment_amount
            if self.salary and self.loan_type_id:
                # loan_configuration_id = self.env['loan.amount.configuration'].search([('loan_type_id','=',self.loan_type_id.id)],limit=1)
                if self.loan_type_id.max_deduction > 0:
                    max_deduction_amount = ((self.salary * self.loan_type_id.max_deduction) / 100)
            if max_deduction_amount > 0 and max_deduction_amount < amount:
                raise ValidationError(_("Maximum Deduction %s Should not Exceed with Installment Amount %s...!")%(str(max_deduction_amount),str(amount)))
            if installment == len(self.loan_lines):
                raise UserError('Error!', 'Line Already Filled')
            else:
                for i in range(1, int(installment) + 1):
                    self.env['hr.loan.line'].create({
                        'date': date_start,
                        'amount': amount,
                        'employee_id': loan.employee_id.id,
                        'loan_id': loan.id,
                        'loan_type_id': loan.loan_type_id.id,
                        'installment_type': loan.installment_type,
                        'desciption': str(loan.desciption) + '-' + str(date_start)})
                    date_start = date_start + relativedelta(months=1)
            # Last Payment Amonuts CA
            for line in loan.loan_lines:
                TotalLastAmount += line.amount
            if (loan.loan_amount - TotalLastAmount) > 0:
                self.env['hr.loan.line'].create({
                    'date': date_start,
                    'amount': loan.loan_amount - TotalLastAmount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id,
                    'loan_type_id': loan.loan_type_id.id,
                    'installment_type': loan.installment_type,
                    'desciption': str(loan.desciption) + '-' + str(date_start)})
        return True


class InstallmentLine(models.Model):
    _name = "hr.loan.line"
    _description = "Installment Line"
    _rec_name = "desciption"
    _order = 'date desc'

    @api.model
    def default_get(self, fields):
        res = super(InstallmentLine, self).default_get(fields)
        LoanObject = self.env['hr.loan'].browse(self._context.get('default_loan_id'))
        res['employee_id'] = LoanObject.employee_id.id
        total = 0.0
        for line in LoanObject.loan_lines:
            total += line.amount
        res['amount'] = LoanObject.loan_amount - total
        return res

    date = fields.Date(string="Payment Date", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    amount = fields.Float(string="Amount", required=True)
    status = fields.Selection([('pending', 'Pending'), ('done', 'Done'), ('hold', 'Hold')], string="Status",
                              default="pending")
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.")
    loan_type_id = fields.Many2one('loan.type', string="Loan Type")
    desciption = fields.Text(string="Description")
    installment_type = fields.Selection([
        ('installment_amount', 'Installment Amount'),
        ('installment_no', 'Installment No.'),
    ], string="Payment Type", copy=False)
    readonly_line = fields.Boolean(compute="_compute_readonly")

    @api.depends('status')
    def _compute_readonly(self):
        """it check the condition and on this condition it'll be readonly"""
        for rec in self:
            if rec.status in ['done','hold']:
                rec.readonly_line = True
            else:
                rec.readonly_line = False

    @api.onchange('date')
    def _onchange_date(self):
        for emp in self:
            emp.desciption = str(emp.loan_id.desciption) + '-' + str(emp.date)

    @api.model
    def create(self, values):
        LoanObject = self.env['hr.loan'].browse(int(values.get('loan_id')))
        desciption = LoanObject.desciption
        date = values.get('date')
        if date:
            values['desciption'] = str(desciption) + '-' + str(date)
        return super(InstallmentLine, self).create(values)

    def write(self, values):
        desciption = self.loan_id.desciption
        date = values.get('date')
        if date:
            values['desciption'] = str(desciption) + '-' + str(date)
        return super(InstallmentLine, self).write(values)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    loan_count = fields.Integer(string="Employee Loan Count", compute='_compute_employee_loans')

    @api.depends('name')
    def _compute_employee_loans(self):
        """This compute the loan amount and total loans count of an employee.
            """
        for rec in self:
            rec.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', rec.id)])
