# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RejectReason(models.TransientModel):
	_name = 'reject.reason'
	_description = 'Reject Reason'

	name = fields.Text(string="Reject Reason")

	#when click on reject button
	def action_reject_apply(self):
		emp_increment_id = self.env['emp.increment'].browse(self.env.context.get('active_ids'))
		emp_increment_id.write({'reject_reason': self.name , 'state' : 'Reject'})
		emp_increment_id.message_post(body="Reject Reason :" + str(self.name))
		return True