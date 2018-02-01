# -*- encoding: utf-8 -*-
# © 2018 Tosin Komolafe @ Ballotnet Solutions Ltd <komolafetosin@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

EXCLUDED_FIELDS = 'create_date create_uid write_date write_uid message_channel_ids message_is_follower \
message_partner_ids message_unread message_unread_counter __last_update display_name doc_count'

class TableCleaner(models.Model):
    _name = 'table.cleaner'
    _description = 'Auto Table Cleaner'

    name = fields.Many2one('ir.model', u'Model')
    cleaner_line_ids = fields.One2many('table.cleaner.line','cleaner_id', string='Cleaner Line', ondelete='cascade')

    def load_fields(self):
    	if self.name:
    		fields = self.env['ir.model.fields'].search([('model','=',self.name.model)])
    		field_names = []
    		views = self.env['ir.ui.view'].search([('model','=',self.name.model)])
    		cleaner_line_obj = self.env['table.cleaner.line']
    		arch_base = EXCLUDED_FIELDS
    		for view in views:
    			arch_base += view.arch_base

    		for field in fields:
    			if field.name not in arch_base:
    				cleaner_line_obj.create({'cleaner_id': self.id, 'field_id': field.id})
    	return True

    def delete_fields(self):
    	if self.name and self.cleaner_line_ids:
    		fields = [c.field_name for c in self.cleaner_line_ids if c.field_name]
    		drop_columns = str()
    		for field in fields:
    			drop_columns += 'DROP COLUMN %s, '%(str(field))

    		drop_columns = drop_columns[::-1].replace(",",";",1)[::-1]
	    	query = "DELETE FROM ir_model_fields WHERE model = %s AND name in %s;"
	    	self.env.cr.execute(query,[self.name.model, tuple(fields)])

    		for field in fields:
    			try:
    				self.env.cr.execute("ALTER TABLE " + self.env[self.name.model]._table + " DROP COLUMN " + field)
    			except:
    				continue
    		self.cleaner_line_ids.unlink()
    		self.env.cr.commit()

    	return True

class TableCleanerLine(models.Model):
	_name = 'table.cleaner.line'
	_description = 'Auto Table Cleaner Line'

	cleaner_id = fields.Many2one('table.cleaner', 'Table Cleaner', ondelete='cascade')
	field_id = fields.Many2one('ir.model.fields', 'Field')
	field_name = fields.Char(related='field_id.name')
	field_type = fields.Selection(related='field_id.ttype')
	field_relation = fields.Char(related='field_id.relation')

	_sql_constraints = [('field_uniq', 'unique (field_id, cleaner_id)', _('Field cannot be duplicated!'))]
        