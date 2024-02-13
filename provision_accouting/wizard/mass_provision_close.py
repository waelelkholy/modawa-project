# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date

class MassProvisionClose(models.TransientModel):
    _name = "mass.provision.close"
    _description = "Mass Provision Close"
    
    department_id = fields.Many2one('hr.department','Department')
    provision_configuration_id = fields.Many2one('provision.configuration',string='Provision Type')
    amount = fields.Float('Amount')
    credit_account_id = fields.Many2one('account.account','Credit Account')
    reason = fields.Char('Reason')

    @api.onchange('department_id','provision_configuration_id')
    def onchange_provision_configuration_id(self):
        if self.provision_configuration_id:
            employee_id = self.env['hr.employee'].search([('department_id','=',self.department_id.id)])
            provision_ids = self.env['account.provision'].search([('state','=','running'),('provision_type_id','=',self.provision_configuration_id.id),('employee_id','=',employee_id.ids if employee_id else False)])
            amount = 0
            for provision_id in provision_ids:
                amount += sum(round(x.value,2) if x.move_id.state == 'posted' else 0 for x in provision_id.provision_line)
            self.amount = amount

    def action_close_provision(self):
        employee_ids = self.env['hr.employee'].search([('department_id','=',self.department_id.id)])
        for employee_id in employee_ids:
            provision_ids = self.env['account.provision'].search([('state','=','running'),('provision_type_id','=',self.provision_configuration_id.id),('employee_id','=',employee_id.id)])
            analytic_account_id = self.env['account.analytic.account'].search([('department_id','=',employee_id.department_id.id)])
            move_id = self.env['account.move'].create({
                'date':date.today(),
                'move_type':'entry',
                'journal_id':self.provision_configuration_id.journal_id.id,
                'ref':'Provision Close ' + employee_id.name + ' ' + self.provision_configuration_id.type,
                'partner_id':employee_id.partner_id.id
            })
            amount = 0
            for provision_id in provision_ids:
                amount += sum(round(x.value,2) if x.move_id.state == 'posted' else 0 for x in provision_id.provision_line)
            move_lines = []
            for i in range(0,2):
                if i==0:
                    move_lines.append({
                        'account_id':self.provision_configuration_id.credit_account_id.id,
                        'name':self.reason+' - Debit',
                        'partner_id':employee_id.partner_id.id,
                        'analytic_account_id':analytic_account_id.id,
                        'debit': round(amount,2),
                    })
                elif i==1:
                    move_lines.append({
                        'account_id':self.credit_account_id.id,
                        'name':self.reason+' - Credit',
#                         'partner_id':self.employee_id.partner_id.id,
                        'analytic_account_id':analytic_account_id.id,
                        'credit': round(amount,2),
                    })
            lines = [(0, 0, line_move) for line_move in move_lines]
            move_id.write({'line_ids':lines})
            for line in move_id.line_ids:
                if line.name.find('Credit') == 0:
                    line.write({'partner_id':employee_id.partner_id.id})
            for provision_id in provision_ids:
                provision_id.write({'state':'close','close_move_id':move_id.id})
