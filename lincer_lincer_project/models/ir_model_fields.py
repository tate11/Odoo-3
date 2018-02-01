# -*- encoding: utf-8 -*-

from odoo import models, api, fields


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    dynamic_view_field = fields.Boolean('Dynamic Fields on Tasks')
