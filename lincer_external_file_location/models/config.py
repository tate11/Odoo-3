# coding: utf-8
# @ 2017 Tosin Komolafe @ Ballotnet Solutions Ltd
#  © @author Tosin Komolafe <komolafetosin@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


class TaskConfig(models.Model):
	_name = 'external.file.task.config'

	model_id = fields.Many2one('ir.model', 'Attachment Model')
	field_id = fields.Many2one('ir.model.fields', 'Attachment Field')
	domain = fields.Text('Domain', default='[]')
	task_id = fields.Many2one('external.file.task', string=u'Task')

	_sql_constraints = [('default_uniq', 'unique(model_id, field_id, domain, task_id)',
		u'Task configuration cannot be repeated!')]