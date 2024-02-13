
from odoo import models, fields, api


class EmployeeIncrementReport(models.AbstractModel):
    # Private attributes
    _name = 'report.emp_increment.employee_increment_template'
    _description = "Employee increment Template"

    # compute and search fields, in the same order of fields declaration
    @api.model
    def _get_report_values(self, docids, data=None):
        """
        return the report
        """

        docs = self.env['emp.increment'].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': 'emp.increment',
            'docs': docs,
        }