# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
from dateutil.relativedelta import relativedelta

class ProvisionClose(models.TransientModel):
    _name = "provision.close"
    _description = "Provision Close"
    
    # Get Default Value
    @api.model
    def default_get(self, fields):
        if self._context.get('payment_request'):
            res = super(ProvisionClose, self).default_get(fields)
            employee_id = self.env['hr.employee'].browse(self._context.get('active_ids'))
            res['peroid'] = relativedelta(date.today(), employee_id.hire_date).years
            res['employee_id'] = employee_id.id if employee_id else False
            return res
        else:
            res = super(ProvisionClose, self).default_get(fields)
            employee_id = self.env['hr.employee'].browse(self._context.get('active_ids'))
            res['peroid'] = relativedelta(date.today(), employee_id.hire_date).years
            res['employee_id'] = employee_id.id if employee_id else False
            res['provision_configuration_id'] = self.env['provision.configuration'].search([], limit=1).id
            return res
    
    employee_id = fields.Many2one('hr.employee','Employee')
    provision_configuration_id = fields.Many2one('provision.configuration',string='Provision Type')
    amount = fields.Float('Amount')
    provision_calculated = fields.Float('Calculated EOSB')
    real_amount = fields.Float('Real Amount')
    peroid = fields.Integer(string='Period Of Service')
    credit_account_id = fields.Many2one('account.account','Credit Account')
    difference_account_id = fields.Many2one('account.account','Difference Account')
    positive_account_id = fields.Many2one('account.account','Difference Account.')
    is_diffirent = fields.Boolean(default=False)
    is_positive = fields.Boolean(default=False)
    reason = fields.Char('Reason')
    not_posted_amt = fields.Float(string='Not Posted Amount')
    
    # change on provision_configuration_id
    @api.onchange('provision_configuration_id')
    def onchange_provision_configuration_id(self):
        if self.provision_configuration_id:
            provision_ids = self.env['account.provision'].search([('state','=','running'),('provision_type_id','=',self.provision_configuration_id.id),('employee_id','=',self.employee_id.id)])
            amount = 0
            not_posted_amt = 0
            for provision_id in provision_ids:
                amount += sum(round(x.value,2) if x.move_id.state == 'posted' else 0 for x in provision_id.provision_line)
                not_posted_amt += sum(round(x.value,2) if x.move_id.state != 'posted' else 0 for x in provision_id.provision_line)
            self.amount = amount
            self.real_amount = amount
            self.not_posted_amt = not_posted_amt
        self.onchange_amount()
        self.onchange_amounts()
    
    # # change on provision_configuration_id
    # @api.onchange('provision_configuration_id')
    # def onchange_provision_configuration_id(self):
    #     if self.provision_configuration_id:
    #         provision_ids = self.env['account.provision'].search([('state','=','draft'),('provision_type_id','=',self.provision_configuration_id.id),('employee_id','=',self.employee_id.id)])
    #         amount = 0
    #         for provision_id in provision_ids:
    #             amount += sum(round(x.value,2) if x.move_id.state == 'posted' else 0 for x in provision_id.provision_line)
    #         self.amount = round(amount,2)
    #         self.provision_calculated = round(amount,2)
    #         self.real_amount = round(amount,2)
    #         if self.peroid <= 5:
    #             amount = round(self.provision_calculated,2) / 2
    #             self.amount = round(amount,2)
    #         elif self.peroid >= 6 and self.peroid < 10:
    #             by_peroid = round(self.provision_calculated,2) / self.peroid
    #             amount_data = []
    #             for i in range(self.peroid - 5):
    #                 amount_data.append(by_peroid)
    #             for i in range(5):
    #                 amount_data.append(by_peroid / 2)
    #             amount = sum(amount_data)
    #             self.amount = round(amount,2)
    #         elif self.peroid >= 10:
    #             self.amount = round(self.provision_calculated,2)
    #     self.onchange_amount()
    #     self.onchange_amounts()
    
    # onchange on amount
    @api.onchange('amount')
    def onchange_amount(self):
        if self:
            if self.amount < self.real_amount:
                self.is_diffirent = True
            else:
                self.is_diffirent = False
    
    # onchange on amount
    @api.onchange('amount')
    def onchange_amounts(self):
        if self:
            if self.amount > self.real_amount:
                self.is_positive = True
            else:
                self.is_positive = False
                
    
    # Close Provision and Create Move
    def action_close_provision(self):
        if not self.provision_configuration_id.type and not self.provision_configuration_id.credit_account_id:
            raise UserError(_("Please Configure Provision Configuration"))
        if self.amount > self.real_amount:
            # raise UserError(_("You can't add More than Total"))
            count = 3 if self.is_positive else False
            move_id = self.env['account.move'].create({
                    'date':date.today(),
                    'move_type':'entry',
                    'journal_id':self.provision_configuration_id.journal_id.id,
                    'ref':'Provision Close ' + self.employee_id.name + ' ' + self.provision_configuration_id.type,
                    'partner_id':self.employee_id.user_id.partner_id.id if self.employee_id.user_id else False
                })
            analytic_account_id = self.env['account.analytic.account'].search([('department_id','=',self.employee_id.department_id.id)],limit=1)
            move_lines = []
            for i in range(count):
                if i==0:
                    move_lines.append({
                        'account_id':self.provision_configuration_id.credit_account_id.id,
                        'name':self.reason+' - Debit' if self.reason else 'Closed Provision' +' - Debit',
#                         'partner_id':self.employee_id.user_id.partner_id.id if self.employee_id.user_id else False,
#                         'analytic_account_id':analytic_account_id.id,
                        'debit': round(self.real_amount,2),
                    })
                elif i==1:
                    move_lines.append({
                        'account_id':self.positive_account_id.id,
                        'name':self.reason+' - Debit' if self.reason else 'Closed Provision' +' - Debit',
#                         'partner_id':self.employee_id.user_id.partner_id.id if self.employee_id.user_id else False,
                        'analytic_account_id':analytic_account_id.id,
                        'debit': round((self.amount - self.real_amount),2),
                    })
                elif i==2:
                    move_lines.append({
                        'account_id':self.credit_account_id.id,
                        'name':self.reason+' - Credit' if self.reason else 'Closed Provision' +' - Credit',
#                         'partner_id':self.employee_id.user_id.partner_id.id if self.employee_id.user_id else False,
#                         'analytic_account_id':analytic_account_id.id,
                        'credit': round(self.amount,2),
                    })
            lines = [(0, 0, line_move) for line_move in move_lines]
            move_id.write({'line_ids':lines})
#             for line in move_id.line_ids:
#                 if line.name.find('Credit') == 0:
#                     line.write({'partner_id':self.employee_id.user_id.partner_id.id if self.employee_id.user_id else False})
            for line in move_id.line_ids:
                if line.account_id.id == self.provision_configuration_id.credit_account_id.id:
                    line.write({'partner_id':self.employee_id.user_id.partner_id.id if self.employee_id.user_id else False})
            provision_ids = self.env['account.provision'].search([('employee_id','=',self.employee_id.id),('state','=','running'),('provision_type_id','=',self.provision_configuration_id.id)])
            for provision_id in provision_ids:
                provision_id.write({'state':'close','close_move_id':move_id.id})
                provision_id.message_post(body='Reason : ' + str(self.reason) if self.reason else 'Closed Provision' + '<br/> Closing Date : ' + str(date.today()))
        else: 
            count = 3 if self.is_diffirent else 2
            move_id = self.env['account.move'].create({
                    'date':date.today(),
                    'move_type':'entry',
                    'journal_id':self.provision_configuration_id.journal_id.id,
                    'ref':'Provision Close ' + self.employee_id.name + ' ' + self.provision_configuration_id.type,
                    'partner_id':self.employee_id.user_id.partner_id.id if self.employee_id.user_id else False
                })
            analytic_account_id = self.env['account.analytic.account'].search([('department_id','=',self.employee_id.department_id.id)])
            move_lines = []
            for i in range(count):
                if i==0:
                    move_lines.append({
                        'account_id':self.provision_configuration_id.credit_account_id.id,
                        'name':self.reason+' - Debit' if self.reason else 'Closed Provision' +' - Debit',
                        'partner_id':self.employee_id.user_id.partner_id.id if self.employee_id.user_id else False,
#                         'analytic_account_id':analytic_account_id.id,
                        'debit': round(self.real_amount,2),
                    })
                elif i==1:
                    move_lines.append({
                        'account_id':self.credit_account_id.id,
                        'name':self.reason+' - Credit' if self.reason else 'Closed Provision' +' - Credit',
#                         'partner_id':self.employee_id.user_id.partner_id.id if self.employee_id.user_id else False,
#                         'analytic_account_id':analytic_account_id.id,
                        'credit': round(self.amount,2),
                    })
                elif i==2:
                    move_lines.append({
                        'account_id':self.difference_account_id.id,
                        'name':self.reason+' - Credit' if self.reason else 'Closed Provision' +' - Credit',
#                         'partner_id':self.employee_id.user_id.partner_id.id if self.employee_id.user_id else False,
#                         'analytic_account_id':analytic_account_id.id,
                        'credit': round((self.real_amount - self.amount),2),
                    })
            lines = [(0, 0, line_move) for line_move in move_lines]
            move_id.write({'line_ids':lines})
            for line in move_id.line_ids:
                if line.name.find('Debit') == 0:
                    line.write({'partner_id':self.employee_id.user_id.partner_id.id if self.employee_id.user_id else False})
            provision_ids = self.env['account.provision'].search([('employee_id','=',self.employee_id.id),('state','=','running'),('provision_type_id','=',self.provision_configuration_id.id)])
            for provision_id in provision_ids:
                provision_id.write({'state':'close','close_move_id':move_id.id})
                provision_id.message_post(body='Reason : ' + str(self.reason) if self.reason else 'Closed Provision' + '<br/> Closing Date : ' + str(date.today()))
    
#     def action_close_provision(self):
#         if self.amount > self.real_amount:
#             # raise UserError(_("You can't add More than Total"))
#             count = 3 if self.is_positive else False
#             move_id = self.env['account.move'].create({
#                     'date':date.today(),
#                     'move_type':'entry',
#                     'journal_id':self.provision_configuration_id.journal_id.id,
#                     'ref':'Provision Close ' + self.employee_id.name + ' ' + self.provision_configuration_id.type,
#                     'partner_id':self.employee_id.user_partner_id.id
#                 })
#             analytic_account_id = self.env['account.analytic.account'].search([('department_id','=',self.employee_id.department_id.id)])
#             move_lines = []
#             for i in range(count):
#                 if i==0:
#                     move_lines.append({
#                         'account_id':self.provision_configuration_id.credit_account_id.id,
#                         'name':self.reason+' - Debit',
# #                         'partner_id':self.employee_id.user_partner_id.id,
#                         'analytic_account_id':analytic_account_id.id,
#                         'debit': round(self.real_amount,2),
#                     })
#                 elif i==1:
#                     move_lines.append({
#                         'account_id':self.positive_account_id.id,
#                         'name':self.reason+' - Debit',
# #                         'partner_id':self.employee_id.user_partner_id.id,
#                         'analytic_account_id':analytic_account_id.id,
#                         'debit': round((self.amount - self.real_amount),2),
#                     })
#                 elif i==2:
#                     move_lines.append({
#                         'account_id':self.credit_account_id.id,
#                         'name':self.reason+' - Credit',
#                         'partner_id':self.employee_id.user_partner_id.id,
#                         'analytic_account_id':analytic_account_id.id,
#                         'credit': round(self.amount,2),
#                     })
#             lines = [(0, 0, line_move) for line_move in move_lines]
#             move_id.write({'line_ids':lines})
#             for line in move_id.line_ids:
#                 if line.name.find('Credit') == 0:
#                     line.write({'partner_id':self.employee_id.user_partner_id.id})
#             for line in move_id.line_ids:
#                 if line.account_id.id == self.provision_configuration_id.credit_account_id.id:
#                     line.write({'partner_id':self.employee_id.user_partner_id.id})
#             provision_ids = self.env['account.provision'].search([('employee_id','=',self.employee_id.id),('state','=','running'),('provision_type_id','=',self.provision_configuration_id.id)])
#             for provision_id in provision_ids:
#                 provision_id.write({'state':'close','close_move_id':move_id.id})
#         else: 
#             count = 3 if self.is_diffirent else 2
#             move_id = self.env['account.move'].create({
#                     'date':date.today(),
#                     'move_type':'entry',
#                     'journal_id':self.provision_configuration_id.journal_id.id,
#                     'ref':'Provision Close ' + self.employee_id.name + ' ' + self.provision_configuration_id.type,
#                     'partner_id':self.employee_id.user_partner_id.id
#                 })
#             analytic_account_id = self.env['account.analytic.account'].search([('department_id','=',self.employee_id.department_id.id)])
#             move_lines = []
#             for i in range(count):
#                 if i==0:
#                     move_lines.append({
#                         'account_id':self.provision_configuration_id.credit_account_id.id,
#                         'name':self.reason+' - Debit',
#                         'partner_id':self.employee_id.user_partner_id.id,
#                         'analytic_account_id':analytic_account_id.id,
#                         'debit': round(self.real_amount,2),
#                     })
#                 elif i==1:
#                     move_lines.append({
#                         'account_id':self.credit_account_id.id,
#                         'name':self.reason+' - Credit',
# #                         'partner_id':self.employee_id.user_partner_id.id,
#                         'analytic_account_id':analytic_account_id.id,
#                         'credit': round(self.amount,2),
#                     })
#                 elif i==2:
#                     move_lines.append({
#                         'account_id':self.difference_account_id.id,
#                         'name':self.reason+' - Credit',
# #                         'partner_id':self.employee_id.user_partner_id.id,
#                         'analytic_account_id':analytic_account_id.id,
#                         'credit': round((self.real_amount - self.amount),2),
#                     })
#             lines = [(0, 0, line_move) for line_move in move_lines]
#             move_id.write({'line_ids':lines})
#             for line in move_id.line_ids:
#                 if line.name.find('Debit') == 0:
#                     line.write({'partner_id':self.employee_id.user_partner_id.id})
#             provision_ids = self.env['account.provision'].search([('employee_id','=',self.employee_id.id),('state','=','running'),('provision_type_id','=',self.provision_configuration_id.id)])
#             for provision_id in provision_ids:
#                 provision_id.write({'state':'close','close_move_id':move_id.id})
