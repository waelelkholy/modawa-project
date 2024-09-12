# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import calendar
from datetime import date
import datetime

class AccountProvision(models.Model):
    _name = 'account.provision'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Provision'
    
    # Get Total Amounts From provision_line(Value)
    @api.depends('provision_line.value')
    def _compute_all_value_for_line(self):
        for data in self:
            data.total_amount = sum([round(x.value,2) for x in data.provision_line])
            data.due_amonut = sum([x.value for x in data.provision_line])
            data.total_amount_posted += sum(round(x.value,2) if x.move_id.state == 'posted' else 0 for x in data.provision_line)

    name = fields.Char('Name')
    provision_type_id = fields.Many2one('provision.configuration',string="Provision Type")
    post_date = fields.Date(string="First Post Date")
    cost_center = fields.Many2one('account.analytic.account',string="Cost Center")
    provision_line = fields.One2many('account.provision.line','provision_id',string="Provision Line")
    employee_id = fields.Many2one('hr.employee','Employee')
    state = fields.Selection([('draft','Draft'),('running','Running'),('close','Close')],string="Status",default="draft")#,('running','Running')
    close_move_id = fields.Many2one('account.move','Close Move')
    # New Added
    total_amount = fields.Float(string='Total Amount',compute='_compute_all_value_for_line')
    due_amonut = fields.Float(string='Due Amount',compute='_compute_all_value_for_line')
    total_amount_posted = fields.Float(string='Total Amount Posted',compute='_compute_all_value_for_line')
    
    # Post Provision line
    def _post_entries(self):
        ProvisionLineIds = self.env['account.provision.line'].search([('end_date','=',date.today()),('move_id','=',False),('state','=','running')])
        for ProvisionLineId in ProvisionLineIds:
            ProvisionLineId.create_move()
    
    # Action Open Journal
    def action_open_journal(self):
        move_ids = []
        for p_line in self.provision_line:
            move_ids.append(p_line.move_id.id)
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', move_ids)],
        }
    
    # Unlink Record
    def unlink(self):
        for rec in self:
            if rec.state in ['running','close']:
                raise UserError(_("You can not delete a Running or a Close Records."))
        return super(AccountProvision,self).unlink()

class AccountProvisionLine(models.Model):
    _name = 'account.provision.line'
    _description = 'Account Provision Line'

    provision_id = fields.Many2one('account.provision',string="Provision Id")
    date = fields.Date(string="Start Date")
    end_date = fields.Date(string="Post Date")
    state = fields.Selection(related="provision_id.state")
    value = fields.Float(string="Value")
    move_id = fields.Many2one('account.move','Move')
    move_check = fields.Boolean(compute='_get_move_check', string='Linked', store=True)
    move_posted_check = fields.Boolean(compute='_get_move_posted_check', string='Posted', store=True)

    # Depends on Move_id
    @api.depends('move_id')
    def _get_move_check(self):
        for line in self:
            line.move_check = bool(line.move_id)
    
    # Depends on move_id.state
    @api.depends('move_id.state')
    def _get_move_posted_check(self):
        for line in self:
            line.move_posted_check = True if line.move_id and line.move_id.state == 'posted' else False
    
    # Create account.move
    def create_move(self, adjustment=False):
        parent_id = self.provision_id
        config_id = parent_id.provision_type_id
        move_id = self.env['account.move'].create({
                'date':self.end_date,
                'move_type':'entry',
                'journal_id':config_id.journal_id.id,
                'ref':parent_id.name + " " + adjustment if adjustment else parent_id.name,
                # 'employee_related': True if adjustment else False,
                'partner_id':parent_id.employee_id.address_home_id.id
            })
        move_lines = []
        for i in range(2):
            if i == 0:
                move_lines.append({
                    'account_id':config_id.debit_account_id.id,
                    'name':'Debit',
                    'partner_id':parent_id.employee_id.address_home_id.id,
                    # 'employee_id':parent_id.employee_id.id,
                    # 'analytic_account_id':parent_id.cost_center.id,
                    'debit': round(self.value,2),
                })
            if i==1:
                move_lines.append({
                    'account_id':config_id.credit_account_id.id,
                    'name': 'Credit',
                    'partner_id':parent_id.employee_id.address_home_id.id,
                    # 'employee_id':parent_id.employee_id.id,
                    # 'analytic_account_id':parent_id.cost_center.id,
                    'credit': round(self.value,2),
                })
        lines = [(0, 0, line_move) for line_move in move_lines]
        move_id.write({'line_ids':lines})
        self.write({'move_id':move_id.id})
        for line in move_id.line_ids:
            if line.name == 'Credit':
                line.write({'partner_id':parent_id.employee_id.address_home_id.id})
