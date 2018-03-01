# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError
import csv
import os
from base64 import b64encode
from datetime import date


class TaskActionLineExport(models.TransientModel):
    """
    This wizard will confirm the all the selected dossie movimentacao task
    """

    _name = "task.action.line.export"
    _description = "Export Action Lines"

    @api.multi
    def export_action_lines(self):
        task = self.env['external.file.task'].search([('method_type','=','export'),('location_id.protocol','in',['ftp', 'sftp'])], limit=1)
        if task:
            context = dict(self._context or {})
            active_ids = context.get('active_ids', []) or []
            base_path = '/tmp/'
            file_name = date.today().isoformat().replace('-','_').replace('/','_') +'_acoes.csv' #current_date(no symbols)_acoes.csv
            full_path = os.path.join(base_path, file_name)
            with open(full_path, 'wb') as csvfile:
                writer = csv.writer(csvfile)
                dict_ids = [[id] for id in active_ids]
                writer.writerows(dict_ids)
            
            with open(full_path, "rb") as csvfile:
                datas = csvfile.read()
            if datas:
                attachment = self.env['ir.attachment'].create({'name':file_name,'datas':b64encode(datas), 
                                                                'datas_fname': file_name,'task_id':task.id,
                                                                'file_type':'export_external_location'})
                attachment.env.cr.commit()
                if attachment:
                    attachment.run()
        else:
            raise UserError('To continue using this export, you need to setup protocol for FTP or SFTP.')
        
        return {'type': 'ir.actions.act_window_close'}