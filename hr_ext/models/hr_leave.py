
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from datetime import timedelta


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    include_holidays = fields.Boolean()


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    #add validation if try to validate behalf of admin
    def action_validate(self):
        if self.state == 'validate1' and not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            raise UserError(_('Only Time Off Admin Can validate it...!'),)
        res = super(HrLeave, self).action_validate()
        return res

    @api.model
    def create(self, values):
        res = super(HrLeave, self).create(values)
        if not res.sudo().employee_id.contract_id or res.sudo().employee_id.contract_id.state != 'open':
            raise UserError(
                _('This Employee Contract not in running state'),
            )
        if res.holiday_status_id and res.holiday_status_id.leave_validation_type in ['manager','both']:
            res._create_activity()
        return res

    #override method to done the activity
    def action_approve(self):
        res = super(HrLeave,self).action_approve()
        for data in self.activity_ids:
            data.action_done()
        return res
        
    #create activity for manager
    def _create_activity(self):
        for data in self.employee_ids:
            if data.parent_id.user_id: 
                res_model_id = self.env['ir.model'].search(
                    [('name', '=', self._description)]).id
                search_mail_activity_id = self.env['mail.activity'].search([('res_id','=',self.id),('user_id','=',data.parent_id.user_id.id)])
                if not search_mail_activity_id:
                    message = "Please approve Time Off :-" + " " +  str(self.holiday_status_id.name) + "which is created by :-" + " " +str(self.env.user.name)
                    self.env['mail.activity'].create([{'activity_type_id': 4,
                                                       'date_deadline': datetime.today(),
                                                       'summary': self.name,
                                                       'create_uid' : self.env.uid,
                                                       'user_id': data.parent_id.user_id.id,
                                                       'res_id': self.id,
                                                       'res_model_id': res_model_id,
                                                       'note': message,
                                                       }])

    include_holidays = fields.Boolean(invisible=1)
    old_employee_no = fields.Char()#related="employee_id.old_employee_number"
    # x_employee_code = fields.Char('Employee Number')
    is_readoly = fields.Boolean(string="Is Readonly")

    #based on configuration make it readonly and auto fetch value
    @api.onchange('holiday_status_id')
    def _onchange_holiday_status_id(self):
        for data in self:
            if data.holiday_status_id and data.holiday_status_id.include_holidays:
                data.include_holidays = data.is_readoly = True
            else:
                data.include_holidays = data.is_readoly = False

    @api.onchange('date_from', 'date_to', 'employee_id', 'include_holidays','holiday_status_id')
    def _onchange_leave_dates(self):
        if self.date_from and self.date_to:
            self.number_of_days = self._get_number_of_days(self.date_from, self.date_to, self.employee_id.id)['days']
            if self.holiday_status_id.include_holidays:
                count = 0.0
                if self.employee_id and self.employee_id.resource_calendar_id:
                    day_count = (self.date_to - self.date_from).days + 1
                    for i in (self.date_from + timedelta(n) for n in range(day_count)):
                        day = int(i.strftime("%w")) - 1
                        if day == -1:
                            day = 6
                        day = str(day)
                        days = []
                        for x in self.employee_id.resource_calendar_id.attendance_ids:
                            if x.dayofweek == str(day) and x.day_period == 'morning':
                                days.append(x.dayofweek)
                        if not day in days:
                            count = count + 1.0
                self.number_of_days = self.number_of_days + count
        else:
            self.number_of_days = 0

class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    # x_employee_code = fields.Char('Old Employee Number')
