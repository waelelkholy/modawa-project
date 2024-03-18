# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError, ValidationError

class ReturnDate(models.TransientModel):
	_name = 'return.date'
	_description = 'Return Date'
	
	date = fields.Date(string="Return Date")

	#while click on confirm button
	def action_confirm(self):
		custody_id = self.env['hr.custody'].browse(self._context.get('active_id'))
		if self.date < custody_id.date_request:
			raise ValidationError(_('Please Give Valid Return Date'))
		custody_id.state = 'returned'
		custody_id.return_date = self.date
		custody_id.custody_name.is_used = False
		custody.custody_name.state = 'free'
		custody.custody_name.employee_id = False