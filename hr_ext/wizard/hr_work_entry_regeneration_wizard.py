# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class HrWorkEntryRegenerationWizard(models.TransientModel):
    _inherit = 'hr.work.entry.regeneration.wizard'

    work_entry_type = fields.Selection([('all_employee', 'All Employee'), ('by_department', 'Department'),('by_employee', 'By Employee'),], string="Work Entry Type")
    department_id = fields.Many2one('hr.department', string="Department ID")
    employee_ids = fields.Many2many('hr.employee', string="Employees")
    employee_id = fields.Many2one('hr.employee', 'Employee', required=False)

    #overriden method to pass data as needed
    @api.depends('validated_work_entry_ids','employee_ids')
    def _compute_valid(self):
        for wizard in self:
            wizard.valid = True

    #fill employee data based on work entry type
    @api.onchange('work_entry_type','department_id')
    def onchange_work_entry_type(self):
        for data in self:
            if data.work_entry_type == 'all_employee':
                search_employee_id = self.env['hr.employee'].search([])
                data.employee_ids = [(6,0, search_employee_id.ids)]
            elif data.work_entry_type == 'by_department' or data.department_id:
                data.employee_ids = [(6,0, [])]
                if data.department_id:
                    search_employee_id = self.env['hr.employee'].search([('department_id','=',data.department_id.id)])
                    data.employee_ids = [(6,0, search_employee_id.ids)]
            elif data.work_entry_type == 'by_employee':
                data.employee_ids = [(6,0, [])]
            # if data.employee_ids:
            data.employee_id = 1
            data.valid = True

    #overriden method to make entry as per custom needed
    def regenerate_work_entries(self):
        self.ensure_one()
        if not self.env.context.get('work_entry_skip_validation'):
            if not self.valid:
                raise ValidationError(_("In order to regenerate the work entries, you need to provide the wizard with an employee_id, a date_from and a date_to. In addition to that, the time interval defined by date_from and date_to must not contain any validated work entries."))

            if self.date_from and self.earliest_available_date and self.latest_available_date:
                if self.date_from < self.earliest_available_date or self.date_to > self.latest_available_date:
                    raise ValidationError(_("The from date must be >= '%(earliest_available_date)s' and the to date must be <= '%(latest_available_date)s', which correspond to the generated work entries time interval.", earliest_available_date=self._date_to_string(self.earliest_available_date), latest_available_date=self._date_to_string(self.latest_available_date)))

        date_from = max(self.date_from, self.earliest_available_date) if self.earliest_available_date else self.date_from
        date_to = min(self.date_to, self.latest_available_date) if self.latest_available_date else self.date_to
        work_entries = self.env['hr.work.entry'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date_stop', '>=', date_from),
            ('date_start', '<=', date_to),
            ('state', '!=', 'validated')])

        work_entries.write({'active': False})
        for employee_data in self.employee_ids:
            entry_from_date = datetime.strftime(date_from, "%Y-%m-%d %H:%M:%S")
            entry_to_date = datetime.strftime(date_to, "%Y-%m-%d 19:59:00")
            search_old_entry_id = self.env['hr.work.entry'].search([('date_start','>=',entry_from_date),('date_stop','<=',entry_to_date),
                                                                ('employee_id','=',employee_data.id),
                                                                ('contract_id','=',employee_data.contract_id.id)])
            search_old_entry_id.unlink()
            employee_data.generate_work_entries(date_from, date_to, True)
            supension_id = self.env['hr.suspension'].search([('employee_id','=',employee_data.id),('state','=','approved')])
            supension_id.update_old_work_entry()
            supension_id.create_work_entry_suspended_employee()
        action = self.env["ir.actions.actions"]._for_xml_id('hr_work_entry.hr_work_entry_action')
        return action
