# -*- encoding: utf-8 -*-
from odoo import fields, api, models, _
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

class TaskAction(models.Model):
    _inherit = 'project.task.action'

    team_type = fields.Selection([('t',u'Single Team'),('d',u'Team Distribution')], default='t', string=u'Team Type')
    distribution_id = fields.Many2one(comodel_name='project.team.distribution',string=u'Team Distribution')


class ProjectTaskActionLine(models.Model):
    _inherit = 'project.task.action.line'

    def get_team_id(self):
        team_id = super(ProjectTaskActionLine, self).get_team_id()
        if self.action_id and self.task_id:
            if self.action_id.team_type =='d':
                for line in self.action_id.distribution_id.team_distribution_line_ids:
                    rule = expression.normalize_domain(safe_eval(line.domain))
                    tasks = self.env['project.task'].search(rule)
                    if self.task_id.id in tasks.ids:
                        team_id = line.team_id.id or False
                        break
                    else:
                        team_id = False
        return team_id

    @api.model
    def create(self, vals):
        action_line = super(ProjectTaskActionLine, self).create(vals)
        if action_line:
            setattr(action_line, 'team_id', action_line.get_team_id())
        return action_line

"""
class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def create(self, vals):
        task  = super(ProjectTask, self).create(vals)
        if task:
            for action_line in task.action_line_ids:
                team_id = action_line.get_team_id(action_line.action_id, task.id)
                if team_id:
                    setattr(action_line, 'team_id', team_id)
        return task
"""
        
class TeamDistributionLine(models.Model):
    _name = 'project.team.distribution.line'
    _description = u'Team Distribution Line'

    team_id = fields.Many2one(comodel_name='project.team', string=u'Team')
    domain = fields.Text('Domain', default='[]')
    team_distribution_id = fields.Many2one(comodel_name='project.team.distribution', string=u'Team Distribution')


class TeamDistribution(models.Model):
    _name = 'project.team.distribution'
    _description = u'Team Distributions'

    name = fields.Char(string=u'Name')
    team_distribution_line_ids = fields.One2many(comodel_name='project.team.distribution.line', inverse_name='team_distribution_id', string=u'Team Distribution Lines')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _('Name must be unique!')),
    ]
