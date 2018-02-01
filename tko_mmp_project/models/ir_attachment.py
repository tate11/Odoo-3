# -*-coding:utf-8-*-
from odoo import models, fields, api


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    dossie_document_type = fields.Selection([('i', u'Inicial'), ('s', u'Sentença'), ('a', u'Acordão'), ('c', u'Citação'), ('o', u'Outro')]
                                            , string=u'Dossiê Tipo Documento')
