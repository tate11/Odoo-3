# -*- encoding: utf-8 -*-

from odoo import models, api, fields
from odoo.exceptions import ValidationError


boolean_selection_vals = [('y', u'Yes'), ('n', u'No')]


class task_type(models.Model):
    _inherit = 'task.type'

    field_ids = fields.Many2many('ir.model.fields', 'task_type_fields_rel', 'fields_id', 'type_id', string='Fields',
                                 domain=[('dynamic_view_field', '=', True)])

class OdooVersion(models.Model):
    _name = 'odoo.version'

    name = fields.Char(u'Nome')

class GitRepository(models.Model):
    _name = 'git.repository'

    name = fields.Char(u'Nome')


class project_task(models.Model):
    _inherit = 'project.task'

    ready_analysis = fields.Selection(string=u'Ready for Analysis?', copy=False, selection=boolean_selection_vals, dynamic_view_field=True)
    ready_analysis_show = fields.Boolean(compute='_get_field_show', string=u'Show Ready for Analysis')

    approved = fields.Selection(string=u'Approved?', copy=False, selection=boolean_selection_vals, dynamic_view_field=True)
    approved_show = fields.Boolean(compute='_get_field_show', string=u'Show Approved')

    validated = fields.Selection(string=u'Validated?', copy=False, selection=boolean_selection_vals, dynamic_view_field=True)
    valitaded_show = fields.Boolean(compute='_get_field_show', string=u'Show Validated')

    cancel_reason = fields.Char(string=u'Cancel Reason', copy=False, dynamic_view_field=True)
    cancel_reason_show = fields.Boolean(compute='_get_field_show', string=u'Cancel Reason')

    test_url = fields.Char(string=u'Test URL', copy=False, dynamic_view_field=True)
    test_url_show = fields.Boolean(compute='_get_field_show', string=u'Test URL Show')

    odoo_version = fields.Many2one('odoo.version', string=u'Odoo Version', dynamic_view_field=True)
    odoo_version_show = fields.Boolean(compute='_get_field_show', string=u'Odoo Version Show')

    ########## Github Integration ##########

    git_branch = fields.Char(string=u'Branch', copy=False, dynamic_view_field=True)
    git_branch_show = fields.Boolean(compute='_get_field_show', string=u'Show Branch')

    git_branch_url = fields.Char(string=u'Branch URL', compute='get_branch_url', dynamic_view_field=True)
    #git_branch_url = fields.Char(string=u'Branch URL', dynamic_view_field=True)
    git_branch_url_show = fields.Boolean(compute='_get_field_show', string=u'Show Branch URL')

    git_repository_id = fields.Many2one('git.repository', string=u'Repository', copy=False, dynamic_view_field=True)
    git_repository_id_show = fields.Boolean(compute='_get_field_show', string=u'Show Git Repository')

    git_pr_master = fields.Char(string=u'Pull Request Master', copy=False, dynamic_view_field=True)
    git_pr_master_show = fields.Boolean(compute='_get_field_show', string=u'Show Pull Request Master')

    git_pr_dev = fields.Char(string=u'Pull Request Dev', copy=False, dynamic_view_field=True)
    git_pr_dev_show = fields.Boolean(compute='_get_field_show', string=u'Show Pull Request Dev')

    @api.one
    @api.depends('git_repository_id', 'git_branch')
    def get_branch_url(self):
        if not self.company_id.git_url:
            raise ValidationError(u'Git URL has not been set for ' + self.company_id.name+"!")      
        if self.git_branch and self.git_repository_id:
            if '/' == self.company_id.git_url[-1]:
                self.git_branch_url = self.company_id.git_url + self.git_repository_id.name + '/tree/' + self.git_branch
            else:
                self.git_branch_url = self.company_id.git_url +'/'+self.git_repository_id.name + '/tree/' + self.git_branch

     
    @api.model
    def create(self, vals):
        res = super(project_task, self).create(vals)
        branch_name = str(res.id) + "/"
        name = str(vals.get('name'))
        start = name.find("[")
        end = name.find("]")
        if start != -1 and end != -1:
            branch_name = branch_name + name[start + 1: end]
 
        self.env.cr.execute("update project_task set git_branch ='%s' where id='%s'" % (branch_name, res.id))
        return res

    # set dynamic_view_field True in fields
    # dynamic_view_field is custom property
    @api.model_cr_context
    def _field_create(self):
        result = super(project_task, self)._field_create()
        model_fields = sorted(self._fields.itervalues(), key=lambda field: field.type == 'sparse')
        for field in model_fields:
            if field._attrs.get('dynamic_view_field'):
                field_id = self.env['ir.model.fields'].search([('name', '=', field.name)], limit=1)
                # can't use write becuase manual fields are not allowed to write
                if field_id:
                    self._cr.execute("update ir_model_fields set dynamic_view_field='t' where id='%s'" % field_id.id)
        return result

    @api.depends('task_type_id', 'task_type_id.field_ids')
    @api.one
    def _get_field_show(self):
        # write name of dynamic field
        dynamic_fields_list = ['ready_analysis', 'approved', 'validated', 'cancel_reason', 'test_url', 'odoo_version',
                               'git_branch', 'git_branch_url', 'git_repository_id', 'git_pr_master', 'git_pr_dev']
        field_names = []
        for field in self.task_type_id.field_ids:
            field_names.append(field.name)
        for field_name in dynamic_fields_list:
            # show the field
            if field_name in field_names:
                field_name += '_show'
                setattr(self, field_name, True)
        return True
