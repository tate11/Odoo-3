# -*- encoding: utf-8 -*-

from odoo import models, api, fields

class Company(models.Model):
    _inherit = 'res.company'
    
    git_url  = fields.Char(u"Git URL")
    
    
    