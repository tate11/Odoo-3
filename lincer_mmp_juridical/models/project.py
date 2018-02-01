# -*-coding:utf-8-*-
from odoo import models, fields, api
from Queue import PriorityQueue
import re
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

boolean_selection_vals = [('s', u'Sim'), ('n', u'Não')]

class ProjectTask(models.Model):
    _inherit = 'project.task'

    default_line_id = fields.Many2one('project.task.default.line', u'Default Line', ondelete='cascade', readonly=True)
    
    @api.model
    def create(self, vals):
        task = super(ProjectTask, self).create(vals)
        if task:
            default_line = self.env['project.task.default.line'].create({'task_id':task.id})
            if default_line:
                task.default_line_id = default_line.id
        return task

    @api.multi
    def write(self, vals):
        task  = super(ProjectTask, self).write(vals)
        default_line = self.env['project.task.default.line'].search([('task_id','=',self.id)])
        if default_line:
            default_line.write({'initial_write':True})
        return task


class ContestacaoPriorityConfig(models.Model):
    _name = 'contestacao.priority.config'
    _description = u"Contestacao Priority Configuration"

    selection_field_id = fields.Many2one('ir.model.fields',u'Selection Field')
    sim_text = fields.Html(u'Sim')
    nao_text = fields.Html(u'Nao')
    priority = fields.Integer('Priority')
    tipo_acao_id = fields.Many2one('dossie.tipo.acao', u'Tipo de Ação')


    _sql_constraints = [('contestacao_priority_config_uniq', 'unique (selection_field_id, priority, tipo_acao_id)',
        u'Selection Field, priority and Tipo must be unique!')
    ]


class ProjectTaskDefault(models.Model):
    _name = 'project.task.default'
    _description = u'Project Task Default'

    html_field_id = fields.Many2one('ir.model.fields', u'HTML Field')
    html_text = fields.Html(u'Text')
    domain = fields.Text('Domain', default='[]')

    _sql_constraints = [('project_task_default_uniq', 'unique (html_field_id, domain)',
        u'Html Field and domain must be unique!')
    ]

class ProjectTaskDefaultLine(models.Model):
    _name = 'project.task.default.line'
    _description = u'Project Task Default Line'

    name = fields.Char(related='task_id.name')
    task_id = fields.Many2one('project.task', u'Task', readonly=True, required=True)

    contestacao_resumo_1 = fields.Html(string="Resumo Contestação 1", readonly=True)
    contestacao_resumo_2 = fields.Html(string="Resumo Contestação 2", readonly=True)
    contestacao_resumo_3 = fields.Html(string="Resumo Contestação 3", readonly=True)

    contestacao_ilegitimidade = fields.Selection(boolean_selection_vals, string=u'Ilegitimidade?', dynamic_view_field=True)
    contestacao_ilegitimidade_show = fields.Boolean(compute='_get_field_show', string=u'Show Ilegitimidade?')
    contestacao_ilegitimidade_text = fields.Html(string="Ilegitimidade")


    contestacao_conexao = fields.Selection(boolean_selection_vals, string=u'Conexão?', dynamic_view_field=True)
    contestacao_conexao_show = fields.Boolean(compute='_get_field_show', string=u'Show Conexão?')
    contestacao_conexao_text = fields.Html(string="Conexão")

    contestacao_litispendencia = fields.Selection(boolean_selection_vals, string=u'Litispendência?', dynamic_view_field=True)
    contestacao_litispendencia_show = fields.Boolean(compute='_get_field_show', string=u'Show Litispendência?')
    contestacao_litispendencia_text = fields.Html(string="Litispendência")


    contestacao_multiplas_acoes = fields.Selection(boolean_selection_vals, string=u'Multiplas ações?', dynamic_view_field=True)
    contestacao_multiplas_acoes_show = fields.Boolean(compute='_get_field_show', string=u'Show Multiplas ações?')
    contestacao_multiplas_acoes_text = fields.Html(string="Multiplas Ações")

    
    contestacao_agressor = fields.Selection(boolean_selection_vals, string=u'Agressor?', dynamic_view_field=True)
    contestacao_agressor_show = fields.Boolean(compute='_get_field_show', string=u'Show Agressor?')
    contestacao_agressor_text = fields.Html(string="Agressor")


    contestacao_justica_gratuita = fields.Selection(boolean_selection_vals, string=u'Justiça gratuita?', dynamic_view_field=True)
    contestacao_justica_gratuita_show = fields.Boolean(compute='_get_field_show', string=u'Show Justiça gratuita?')
    contestacao_justica_gratuita_text = fields.Html(string="Justiça Gratuita")


    contestacao_sumula_385 = fields.Selection(boolean_selection_vals, string=u'Súmula 385/STJ?', dynamic_view_field=True)
    contestacao_sumula_385_show = fields.Boolean(compute='_get_field_show', string=u'Show Súmula 385/STJ?')
    contestacao_sumula_385_text = fields.Html(string="Súmula 385/STJ")
    contestacao_sumula_385_text_no = fields.Html(string="Súmula 385/STJ")


    contestacao_sumula_479 = fields.Selection(boolean_selection_vals, string=u'Súmula 479/STJ?', dynamic_view_field=True)
    contestacao_sumula_479_show = fields.Boolean(compute='_get_field_show', string=u'Show Súmula 479/STJ? (Fraude)')
    contestacao_sumula_479_text = fields.Html(string="Súmula 479/STJ")


    contestacao_reclamacao_atendida = fields.Selection(boolean_selection_vals, string=u'Reclamação atendida?', dynamic_view_field=True)
    contestacao_reclamacao_atendida_show = fields.Boolean(compute='_get_field_show', string=u'Show Reclamação atendida?')
    contestacao_reclamacao_atendida_text = fields.Html(string="Reclamação Atendida")
    contestacao_reclamacao_atendida_text_no = fields.Html(string="Reclamação Atendida")

    contestacao_incompetencia_jec = fields.Selection(boolean_selection_vals, string=u'Incompetência do JEC?', dynamic_view_field=True)
    contestacao_incompetencia_jec_show = fields.Boolean(compute='_get_field_show', string=u'Show Incompetência do JEC?')
    contestacao_incompetencia_jec_text = fields.Html(string="Incompetência do JEC")


    contestacao_aderencia_parecer = fields.Selection(boolean_selection_vals, string=u'Aderência Parecer?', dynamic_view_field=True)
    contestacao_aderencia_parecer_show = fields.Boolean(compute='_get_field_show', string=u'Show Aderência Parecer?')
    contestacao_aderencia_parecer_text = fields.Html(string="Aderência Parecer")


    contestacao_onus = fields.Selection(boolean_selection_vals, string=u'Onus?', dynamic_view_field=True)
    contestacao_onus_show = fields.Boolean(compute='_get_field_show', string=u'Show Onus?')
    contestacao_onus_text = fields.Html(string="Onus")


    contestacao_exercicio_regular = fields.Selection(boolean_selection_vals, string=u'Exercicio regular?', dynamic_view_field=True)
    contestacao_exercicio_regular_show = fields.Boolean(compute='_get_field_show', string=u'Show Exercicio regular?')
    contestacao_exercicio_regular_text = fields.Html(string="Exercicio Regular")


    contestacao_pacta_sunt_servanda = fields.Selection(boolean_selection_vals, string=u'Pacta sunt servanda?', dynamic_view_field=True)
    contestacao_pacta_sunt_servanda_show = fields.Boolean(compute='_get_field_show', string=u'Show Pacta sunt servanda?')
    contestacao_pacta_sunt_servanda_text = fields.Html(string="Pacta Sunt Servanda")


    contestacao_mero_agente = fields.Selection(boolean_selection_vals, string=u'Mero agente?', dynamic_view_field=True)
    contestacao_mero_agente_show = fields.Boolean(compute='_get_field_show', string=u'Show Mero agente?')
    contestacao_mero_agente_text = fields.Html(string="Mero Agente")
    

    contestacao_falta_prova = fields.Selection(boolean_selection_vals, string=u'Falta de prova?', dynamic_view_field=True)
    contestacao_falta_prova_show = fields.Boolean(compute='_get_field_show', string=u'Show Falta de prova?')
    contestacao_falta_prova_text = fields.Html(string="Falta de Prova")

    
    contestacao_cessao = fields.Selection(boolean_selection_vals, string=u'Cessão?', dynamic_view_field=True)
    contestacao_cessao_show = fields.Boolean(compute='_get_field_show', string=u'Show Cessão?')
    contestacao_cessao_text = fields.Html(string="Cessão")

    
    contestacao_previsao_contratual = fields.Selection(boolean_selection_vals, string=u'Previsão contratual?', dynamic_view_field=True)
    contestacao_previsao_contratual_show = fields.Boolean(compute='_get_field_show', string=u'Show Previsão contratual?')
    contestacao_previsao_contratual_text = fields.Html(string="Previsão Contratual")

    
    contestacao_guarda_informacoes = fields.Selection(boolean_selection_vals, string=u'Guarda de informações?', dynamic_view_field=True)
    contestacao_guarda_informacoes_show = fields.Boolean(compute='_get_field_show', string=u'Show Guarda de informações?')
    contestacao_guarda_informacoes_text = fields.Html(string="Guarda de Informações")

    
    contestacao_fato_terceiro = fields.Selection(boolean_selection_vals, string=u'Fato de terceiro?', dynamic_view_field=True)
    contestacao_fato_terceiro_show = fields.Boolean(compute='_get_field_show', string=u'Show Fato de terceiro?')
    contestacao_fato_terceiro_text = fields.Html(string="Fato de Terceiro")

    
    contestacao_inversao_onus_prova = fields.Selection(boolean_selection_vals, string=u'Inversão onus da prova?', dynamic_view_field=True)
    contestacao_inversao_onus_prova_show = fields.Boolean(compute='_get_field_show', string=u'Show Inversão onus da prova?')
    contestacao_inversao_onus_prova_text = fields.Html(string="Inversão Onus da Prova")

    
    contestacao_danos_materias = fields.Selection(boolean_selection_vals, string=u'Danos materiais?', dynamic_view_field=True)
    contestacao_danos_materias_show = fields.Boolean(compute='_get_field_show', string=u'Show Danos materiais?')
    contestacao_danos_materias_text = fields.Html(string="Danos Materiais")

    
    contestacao_devolucao_dobro = fields.Selection(boolean_selection_vals, string=u'Devolução em dobro?', dynamic_view_field=True)
    contestacao_devolucao_dobro_show = fields.Boolean(compute='_get_field_show', string=u'Show Devolução em dobro?')
    contestacao_devolucao_dobro_text = fields.Html(string="Devolução em Dobro")

    
    contestacao_mero_aborrecimento = fields.Selection(boolean_selection_vals, string=u'Mero aborrecimento?', dynamic_view_field=True)
    contestacao_mero_aborrecimento_show = fields.Boolean(compute='_get_field_show', string=u'Show Mero aborrecimento?')
    contestacao_mero_aborrecimento_text = fields.Html(string="Mero Aborrecimento")

    
    contestacao_litigancia_ma_fe = fields.Selection(boolean_selection_vals, string=u'Litigância má-fé?', dynamic_view_field=True)
    contestacao_litigancia_ma_fe_show = fields.Boolean(compute='_get_field_show', string=u'Show Litigância má-fé?')
    contestacao_litigancia_ma_fe_text = fields.Html(string="Litigância Má-fé")

    
    contestacao_dano_moral = fields.Selection(boolean_selection_vals, string=u'Dano moral?', dynamic_view_field=True)
    contestacao_dano_moral_show = fields.Boolean(compute='_get_field_show', string=u'Show Dano moral?')
    contestacao_dano_moral_text = fields.Html(string="Dano Moral")

    
    contestacao_dano_moral_pj = fields.Selection(boolean_selection_vals, string=u'Dano moral PJ?', dynamic_view_field=True)
    contestacao_dano_moral_pj_show = fields.Boolean(compute='_get_field_show', string=u'Show Dano moral PJ?')
    contestacao_dano_moral_pj_text = fields.Html(string="Dano Moral PJ")

    
    contestacao_reclamacao_previa = fields.Selection(boolean_selection_vals, string=u'Reclamação Prévia?', dynamic_view_field=True)
    contestacao_reclamacao_previa_show = fields.Boolean(compute='_get_field_show', string=u'Show Reclamação Prévia')
    contestacao_reclamacao_previa_text = fields.Html(string="Reclamação Prévia")
    contestacao_reclamacao_previa_text_no = fields.Html(string="Reclamação Prévia")
    
    
    contestacao_consiganacao = fields.Selection(boolean_selection_vals, string=u'Consiganação?', dynamic_view_field=True)
    contestacao_consiganacao_show = fields.Boolean(compute='_get_field_show', string=u'Show Consiganação?')
    contestacao_consiganacao_text = fields.Html(string="Consiganação")
    contestacao_consiganacao_text_no = fields.Html(string="Consiganação")

    
    contestacao_tac_tec_tc = fields.Selection(boolean_selection_vals, string=u'TAC/TEC/TC?', dynamic_view_field=True)
    contestacao_tac_tec_tc_show = fields.Boolean(compute='_get_field_show', string=u'Show TAC/TEC/TC')
    contestacao_tac_tec_tc_text = fields.Html(string="TAC/TEC/TC")

    
    contestacao_ta = fields.Selection(boolean_selection_vals, string=u'TA?', dynamic_view_field=True)
    contestacao_ta_show = fields.Boolean(compute='_get_field_show', string=u'Show TA')
    contestacao_ta_text = fields.Html(string="TA")
    
    contestacao_iof = fields.Selection(boolean_selection_vals, string=u'IOF?', dynamic_view_field=True)
    contestacao_iof_show = fields.Boolean(compute='_get_field_show', string=u'Show IOF')
    contestacao_iof_text = fields.Html(string="IOF")

    
    contestacao_capitalizacao_mensal = fields.Selection(boolean_selection_vals, string=u'Capitalização mensal?', dynamic_view_field=True)
    contestacao_capitalizacao_mensal_show = fields.Boolean(compute='_get_field_show', string=u'Show Capitalização mensal')
    contestacao_capitalizacao_mensal_text = fields.Html(string="Capitalização Mensal")

    
    contestacao_cobranca_juros = fields.Selection(boolean_selection_vals, string=u'Cobrança de juros?', dynamic_view_field=True)
    contestacao_cobranca_juros_show = fields.Boolean(compute='_get_field_show', string=u'Show Cobrança de juros')
    contestacao_cobranca_juros_text = fields.Html(string="Cobrança de Juros")

    
    contestacao_comissao_permanencia = fields.Selection(boolean_selection_vals, string=u'Comissão de permanência?', dynamic_view_field=True)
    contestacao_comissao_permanencia_show = fields.Boolean(compute='_get_field_show', string=u'Show Comissão de permanência')
    contestacao_comissao_permanencia_text = fields.Html(string="Comissão de Permanência")

    
    contestacao_posse = fields.Selection(boolean_selection_vals, string=u'Posse?', dynamic_view_field=True)
    contestacao_posse_show = fields.Boolean(compute='_get_field_show', string=u'Show Posse?')
    contestacao_posse_text = fields.Html(string="Posse")

    
    contestacao_restritivos = fields.Selection(boolean_selection_vals, string=u'Restritivos?', dynamic_view_field=True)
    contestacao_restritivos_show = fields.Boolean(compute='_get_field_show', string=u'Show Restritivos?')
    contestacao_restritivos_text = fields.Html(string="Restritivos")

    contestacao_tese = fields.Html(string="Tese")


    recurso_juntada_documentos = fields.Selection(boolean_selection_vals, string=u'Juntada de documentos?', dynamic_view_field=True)
    recurso_juntada_documentos_show = fields.Boolean(compute='_get_field_show', string=u'Show Juntada de documentos?')
    recurso_juntada_documentos_text = fields.Html(string="Juntada de Documentos")


    recurso_documentos_juntados = fields.Selection(boolean_selection_vals, string=u'Documentos Juntados?', dynamic_view_field=True)
    recurso_documentos_juntados_show = fields.Boolean(compute='_get_field_show', string=u'Show Documentos Juntados?')
    recurso_documentos_juntados_text = fields.Html(string="Documentos Juntados")


    recurso_negativacao_preexistente = fields.Selection(boolean_selection_vals, string=u'Negativação preexistente?', dynamic_view_field=True)
    recurso_negativacao_preexistente_show = fields.Boolean(compute='_get_field_show', string=u'Show Negativação preexistente?')
    recurso_negativacao_preexistente_text = fields.Html(string="Negativação Preexistente")


    recurso_danos_morais = fields.Selection(boolean_selection_vals, string=u'Danos morais?', dynamic_view_field=True)
    recurso_danos_morais_show = fields.Boolean(compute='_get_field_show', string=u'Show Danos morais?')
    recurso_danos_morais_text = fields.Html(string="Danos Morais")


    recurso_danos_materiais = fields.Selection(boolean_selection_vals, string=u'Danos materiais?', dynamic_view_field=True)
    recurso_danos_materiais_show = fields.Boolean(compute='_get_field_show', string=u'Show Danos materiais?')
    recurso_danos_materiais_text = fields.Html(string="Danos Materiais")


    prazo_corpo = fields.Html(string="Corpo do Prazo", dynamic_view_field=True)
    prazo_corpo_show = fields.Boolean(compute='_get_field_show', string=u'Show Corpo do Prazo')


    inicial_corpo = fields.Html(string="Corpo da Inicial", dynamic_view_field=True)
    inicial_corpo_show = fields.Boolean(compute='_get_field_show', string=u'Show Corpo da Incial')

    initial_write = fields.Boolean(string=u'Initial Write', default='f', readonly=True)

    
    @api.model_cr_context
    def _field_create(self):
        result = super(ProjectTaskDefaultLine, self)._field_create()
        model_fields = sorted(self._fields.itervalues(),key=lambda field: field.type == 'sparse')
        for field in model_fields:
            if field._attrs.get('dynamic_view_field'):
                field_id = self.env['ir.model.fields'].search([('name', '=', field.name), ('model','=','project.task.default.line')], limit=1)
                if field_id:
                    self._cr.execute("update ir_model_fields set dynamic_view_field='t' where id='%s'" % field_id.id)
        return result


    @api.depends('task_id')
    @api.one
    def _get_field_show(self):
        dynamic_fields_list = ['contestacao_ilegitimidade','contestacao_conexao','contestacao_litispendencia',
        'contestacao_multiplas_acoes','contestacao_agressor','contestacao_justica_gratuita',
        'contestacao_sumula_385','contestacao_sumula_479','contestacao_reclamacao_atendida',
        'contestacao_incompetencia_jec','contestacao_aderencia_parecer','contestacao_onus', 
        'contestacao_exercicio_regular', 'contestacao_pacta_sunt_servanda', 'contestacao_mero_agente',
        'contestacao_falta_prova','contestacao_cessao','contestacao_previsao_contratual',
        'contestacao_guarda_informacoes','contestacao_fato_terceiro',
        'contestacao_inversao_onus_prova','contestacao_danos_materias','contestacao_devolucao_dobro',
        'contestacao_mero_aborrecimento','contestacao_litigancia_ma_fe','contestacao_dano_moral',
        'contestacao_dano_moral_pj','contestacao_reclamacao_previa','contestacao_consiganacao',
        'contestacao_tac_tec_tc','contestacao_ta','contestacao_iof',
        'contestacao_capitalizacao_mensal','contestacao_cobranca_juros','contestacao_comissao_permanencia',
        'contestacao_posse','contestacao_restritivos', 'recurso_juntada_documentos', 'recurso_documentos_juntados', 
        'recurso_negativacao_preexistente', 'recurso_danos_morais', 'recurso_danos_materiais', 'prazo_corpo', 'inicial_corpo',
        ]

        field_names = []
        for field in self.task_id.task_type_id.field_ids:
            field_names.append(field.name)
        for field_name in dynamic_fields_list:
            # show the field
            if field_name in field_names:
                field_name += '_show'
                setattr(self, field_name, True)
        return True

    def __set_defaults__(self, default_line):
        field_names = []
        field_ids = self.env['ir.model.fields'].search([('ttype','=','html'),('model','=','project.task.default.line')])
        for field in field_ids:
            field_names.append(field.name)
        defaults = self.env['project.task.default'].search([('html_field_id.name','in',field_names)])
        for default in defaults:
            rule = expression.normalize_domain(safe_eval(default.domain))
            domain_tasks = self.env['project.task'].search(rule)
            if domain_tasks and default_line.task_id.id in domain_tasks.ids:
                setattr(default_line, default.html_field_id.name, default.html_text)
        return default_line

    def cleanhtml(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext


    def __set_contestacao__(self):
        field_names = []
        queue = PriorityQueue()
        result1 = result2 = result3 = False
        field_ids = self.env['ir.model.fields'].search([('ttype','=','selection'), ('name','ilike','contestacao'), ('model','=','project.task.default.line')])
        for field in field_ids:
            field_names.append(field.name)
        contestacao = self.env['contestacao.priority.config'].search([('selection_field_id.name','in',field_names)])

        for c in contestacao:
            queue.put((c.priority, c))

        limit = 3
        results = []
        while not queue.empty() and limit > 0:
            config = queue.get()
            
            if self.task_id.tipo_acao_id != config[1].tipo_acao_id:
                continue
            
            task_selection_field = getattr(self, config[1].selection_field_id.name, False)

            if task_selection_field =='s' and config[1].sim_text and self.cleanhtml(config[1].sim_text) != '':
                results.append(config[1].sim_text)
                limit -= 1
                continue

            if task_selection_field =='n' and config[1].nao_text and self.cleanhtml(config[1].nao_text) != '':
                results.append(config[1].nao_text)
                limit -= 1
                continue

        result_len = len(results)
        result1 = result_len > 0 and results[0] or False
        result2 = result_len > 1 and results[1] or False
        result3 = result_len > 2 and results[2] or False
        return result1, result2, result3
    
    @api.model
    def create(self, vals):
        default_line = super(ProjectTaskDefaultLine, self).create(vals)
        if default_line:
            self.__set_defaults__(default_line)
        return default_line

    @api.multi
    def write(self, vals):
        super(ProjectTaskDefaultLine, self).write(vals)
        resumo_1, resumo_2, resumo_3 = self.__set_contestacao__()
        vals = {'contestacao_resumo_1':resumo_1,'contestacao_resumo_2':resumo_2,'contestacao_resumo_3':resumo_3}
        return super(ProjectTaskDefaultLine, self).write(vals)
