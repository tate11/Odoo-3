# -*-coding:utf-8-*-
from odoo import models, fields, api

class DossieDossie(models.Model):
    _inherit = 'dossie.dossie'

    def _update_attachment(self, record, vals):
        task = self.env['external.file.task'].search([('method_type','=','export')], limit=1)
        if task:
            fields = self.env['ir.model.fields'].search( [('model', '=', 'dossie.dossie'),('relation','=','ir.attachment')])
            for f in fields:
                if f.name in vals.keys():
                    field_ids = vals.get(f.name)
                    if field_ids:
                        if type(field_ids) is list:
                            attachments = self.env['ir.attachment'].search([('id','in',field_ids[0][2])])
                            if attachments:
                                attachments.write({'res_field':f.name, 'res_id':record.id, 'task_id':task.id})
                        else:
                            attachment = self.env['ir.attachment'].search([('id','=',int(field_ids))])
                            if attachment:
                                attachment.write({'res_field':f.name, 'res_id':record.id, 'task_id':task.id})
        return True

    @api.model
    def create(self, vals):
        res = super(DossieDossie, self).create(vals)
        self._update_attachment(res, vals)
        return res

    @api.multi
    def write(self, vals):

    	for record in self:
    		self._update_attachment(record, vals)
    	return super(DossieDossie, self).write(vals)


class DossieSentenca(models.Model):
    _inherit = 'dossie.sentenca'

    def _update_attachment(self, record, vals):
        task = self.env['external.file.task'].search([('method_type','=','export')], limit=1)
        if task:
            fields = self.env['ir.model.fields'].search( [('model', '=', 'dossie.sentenca'),('relation','=','ir.attachment')])
            for f in fields:
                if f.name in vals.keys():
                    field_ids = vals.get(f.name)
                    if field_ids:
                        if type(field_ids) is list:
                            attachments = self.env['ir.attachment'].search([('id','in',field_ids[0][2])])
                            if attachments:
                                attachments.write({'res_field':f.name, 'res_id':record.id, 'task_id':task.id})
                        else:
                            attachment = self.env['ir.attachment'].search([('id','=',int(field_ids))])
                            if attachment:
                                attachment.write({'res_field':f.name, 'res_id':record.id, 'task_id':task.id})
        return True

    @api.model
    def create(self, vals):
        res = super(DossieSentenca, self).create(vals)
        self._update_attachment(res, vals)
        return res

    @api.multi
    def write(self, vals):
        for record in self:
            self._update_attachment(record, vals)
        return super(DossieSentenca, self).write(vals)
