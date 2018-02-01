# coding: utf-8
# @ 2017 Tosin Komolafe @ Ballotnet Solutions Ltd
#  © @author Tosin Komolafe <komolafetosin@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import base64
import hashlib
import logging
import odoo
from odoo import _, api, fields, models
from odoo.exceptions import UserError
import os


_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    internal_hash = fields.Char(
        readonly=True, store=True, compute='_compute_hash',
        help="File hash computed with file data to be compared "
             "to external hash when provided.")
    external_hash = fields.Char(readonly=True, 
        help="File hash comes from the external owner of the file.\n"
             "If provided allow to check than downloaded file "
             "is the exact copy of the original file.")
    file_type = fields.Selection(
        selection=[('export_external_location','Export File (External location)')],
        string="File type",
        help="The file type determines an import method to be used "
        "to parse and transform data before their import in ERP or an export")
    sync_date = fields.Datetime(readonly=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('done', 'Done'),
        ], readonly=False, required=True, default='pending')
    state_message = fields.Text(readonly=True)
    task_id = fields.Many2one('external.file.task', string='Task')
    location_id = fields.Many2one(
        'external.file.location', string='Location',
        related='task_id.location_id', store=True, readonly=True)

    @api.depends('datas', 'external_hash')
    def _compute_hash(self):
        for attachment in self:
            if attachment.datas:
                attachment.internal_hash = hashlib.md5(
                    base64.b64decode(attachment.datas)).hexdigest()
            if attachment.external_hash and\
               attachment.internal_hash != attachment.external_hash:
                raise UserError(
                    _("File corrupted: Something was wrong with "
                      "the retrieved file, please relaunch the task."))
    
    @api.model
    def create(self, vals):
        attachment = super(IrAttachment, self).create(vals)
        #if attachment:
        #    continue
        return attachment

    @api.model
    def run_attachment_metadata_scheduler(self, domain=None):
        if domain is None:
            domain = [('state', '=', 'pending')]
        attachments = self.search(domain)
        if attachments:
            return attachments.run()
        return True

    @api.multi
    def run(self):
        """
        Run the process for each attachment metadata
        """
        for attachment in self:
            with api.Environment.manage():
                with odoo.registry(self.env.cr.dbname).cursor() as new_cr:
                    new_env = api.Environment(
                        new_cr, self.env.uid, self.env.context)
                    attach = attachment.with_env(new_env)
                    try:
                        attach._run()
                    except Exception, e:
                        attach.env.cr.rollback()
                        _logger.exception(e)
                        attach.write(
                            {
                                'state': 'failed',
                                'state_message': e,
                            })
                        attach.env.cr.commit()
                    else:
                        vals = {
                            'state': 'done',
                            'sync_date': fields.Datetime.now(),
                        }
                        attach.write(vals)
                        attach.env.cr.commit()
        return True

    @api.multi
    def _run(self):
        self.ensure_one()
        _logger.info('Start to process attachment metadata id %s' % self.id)
        if self.file_type == 'export_external_location':
            protocols = self.env['external.file.location']._get_classes()
            location = self.location_id
            cls = protocols.get(location.protocol)[1]
            path = os.path.join(self.task_id.filepath, self.datas_fname)
            with cls.connect(location) as conn:
                datas = base64.decodestring(self.datas)
                conn.setcontents(path, data=datas)

    @api.multi
    def set_done(self):
        """
        Manually set to done
        """
        message = "Manually set to done by %s" % self.env.user.name
        self.write({'state_message': message, 'state': 'done'})
