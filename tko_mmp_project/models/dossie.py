# -*-coding:utf-8-*-
from odoo import models, fields, api, _
import logging
import multiprocessing
import time
import threading
import odoo
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

_SEMAPHORES_POOL = threading.BoundedSemaphore(multiprocessing.cpu_count())


tipo_processo_vals = [('d', u'Digital'), ('f', u'Físico')]
parecer_vals = [('d', u'Defesa'), ('a', u'Acordo'), ('de', u'Decurso de prazo'), ('s', u'Sem Parecer')]
responsabilidade_vals = [('c', u'Cedente'), ('cs', u'Cessionaria'), ('a', 'Em Análise')]
dossie_state = [('m', u'Migrado'), ('a', u'Ativo'), ('s', u'Suspenso'), ('e', u'Encerrado')]
assuncao_defesa_vals = [('c', u'Cedente'), ('ce', u'Cessionária'), ('cc', u'Cendente e Cessionária')]
risco_vals = [('r', u'Remoto'), ('p', u'Possível'), ('pr', u'Provável'), ('a', u'Em Análise')]
polo_cliente_vals = [('a', u'Ativo'), ('p', u'Passivo')]
analise_acordo_vals = [('a', u'Apto'), ('i', u'Inapto')]
dossie_tipo_pagamento_vals = [('p', u'Pagamento'), ('h', u'Honorários'), ('c', u'Custas')]
dossie_resultado_negociacao_vals = [('f', u'Frutífero'), ('i', u'Infrutífero')]
dossie_garantia_status_vals = [('g', u'Garantia'), ('p', u'Pedido de Bloqueio'), ('r', u'Retomado')]
dossie_garantia_tipo_vals = [('i', u'Imóvel'), ('v', u'Veículo'), ('a', u'Avalista')]
boolean_selection_vals = [('s', u'Sim'), ('n', u'Não')]
dossie_movimentacao_tipo_vals = [('a', u'Andamento'), ('p', u'Publicação')]
dossie_movimentacao_resultado_vals = [('nf', u'Nada a Fazer'), ('af', u'Algo a Fazer')]
dossie_penhora_state_vals = [('ad', u'Aguardando Deferimento'), ('ae', u'Aguardando Expedição'), ('ae', u'Aguardando Efetivação'), ('pp', u'Parcialmente Penhorado'), ('p', u'Penhorado'), ('np', u'Não Penhorado')]
analise_historico_state_vals = [('slcj', u'Sem Litispendência ou Coisa Julgada'), ('pl', u'Possível Litispendência'), ('pcj', u'Possível Coisa Julgada'), ('plcj', u'Possível Litispendência ou Coisa Julgada')]
tipo_condenacao_vals = [('p', u'Pagamento'), ('o', u'Obrigação'), ('po', 'Pagamento e Obrigação')]
multa_selection_vals = [('cm', u'Com Multa'), ('sm', u'Sem Multa')]

########## DOSSIÊ ##########


class DossieDossie(models.Model):
    _name = 'dossie.dossie'
    _description = u'Dossiê'

    pasta_cppro = fields.Char(
        string=u'Pasta CPPró')

    ########## CADASTRO ##########

    name = fields.Char(
        string=u'Dossiê')
    carteira_id = fields.Many2one(
        comodel_name='dossie.carteira', 
        string=u'Carteira')
    projeto_id = fields.Many2one(
        comodel_name='project.project', 
        string=u'Projeto')
    credenciado_id = fields.Many2one(
        comodel_name='res.partner', 
        string=u'Credenciado')
    processo = fields.Char(
        string=u'Processo Nº')
    ordinal = fields.Integer(
        string=u'Nº Ordinal')
    comarca_id = fields.Many2one(
        comodel_name='res.state.city', 
        string=u'Comarca')
    estado_id = fields.Many2one(
        comodel_name='res.country.state', 
        string=u'UF')
    vara_id = fields.Many2one(
        comodel_name='dossie.vara', 
        string=u'Vara')
    orgao_id = fields.Many2one(
        comodel_name='dossie.orgao', 
        string=u'Órgão')
    origem_id = fields.Many2one(
        comodel_name='dossie.origem', 
        string=u'Origem')
    polo_cliente = fields.Selection(
        selection=polo_cliente_vals, 
        string=u'Polo do Cliente')
    tipo_processo = fields.Selection(
        selection=tipo_processo_vals,
        string=u'Tipo do Processo')
    fase_id = fields.Many2one(
        comodel_name='dossie.fase', 
        string=u'Fase Atual')
    fase_id_bkp = fields.Many2one(
        comodel_name='dossie.fase', 
        string=u'Fase Anterior')
    responsabilidade = fields.Selection(
        selection=responsabilidade_vals, 
        string=u'Responsabilidade')
    motivo_cadastro_id = fields.Many2one(
        comodel_name='dossie.motivo.cadastro', 
        string=u'Motivo de Cadastro')
    data_cadastro_cliente = fields.Date(
        string=u'Data do Cadastro Cliente')
    assuncao_defesa = fields.Selection(
        selection=assuncao_defesa_vals, 
        string=u'Assunção de Defesa')
    contrato = fields.Char( 
        string=u'Contratos')
    contrato_id = fields.Many2one(
        comodel_name='dossie.contrato', 
        string=u'Contrato')
    contrato_tipo_id = fields.Many2one( 
        string=u'Tipo do Contrato', 
        store=True,
        related='contrato_id.tipo_id')
    numero_pendencias = fields.Integer(
        string=u'Nº Pendencias', 
        compute='get_numero_pendencias', 
        store=False,
        search='search_numero_pendencias')
    cessionaria_id = fields.Many2one( 
        comodel_name=u'res.partner',
        string=u'Cessionária')
    juiz_id = fields.Many2one(
        comodel_name='res.partner',
        string=u'Juiz')

    ########## SITUAÇÃO ##########

    state = fields.Selection(
        selection=dossie_state, 
        default='a', 
        string=u'Estado')
    rito_id = fields.Many2one(
        comodel_name='dossie.rito', 
        string=u'Rito')

    ########## PARTES ##########

    grupo_id = fields.Many2one(
        comodel_name='res.partner', 
        string=u'Grupo')
    parte_representada_ids = fields.Many2many(
        comodel_name='res.partner', 
        relation='dossie_cliente_rel', 
        column1='dossie_id', 
        column2='cliente_id',
        string=u'Parte Representada')
    parte_representada_count = fields.Integer(
        compute='_compute_parte_representada_count', 
        string='Número de Parte Representadas')
    related_parte_representada_ids = fields.Many2many(
        string=u'Parte Representada Related',
        related='parte_representada_ids')
    parte_contraria_ids = fields.Many2many(
        comodel_name='res.partner', 
        relation='dossie_parte_contraria_rel', 
        column1='dossie_id', 
        column2='parte_id',
        string=u'Parte Contrária')
    related_parte_contraria_ids = fields.Many2many(
        string=u'Parte Contrária Related', 
        related='parte_contraria_ids')
    parte_contraria_contumaz_ids = fields.Many2many(
        comodel_name='res.partner', 
        relation='dossie_parte_contraria_contumaz_rel', 
        column1='dossie_id',
        column2='parte_id',
        string=u'Contumazes', 
        compute='get_parte_contraria_contumaz_ids')
    tem_advogado = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Tem Advogado')
    escritorio_id = fields.Many2one(
        comodel_name='res.partner', 
        string=u'Escritório')
    advogado_adverso_ids = fields.Many2many(
        comodel_name='res.partner', 
        relation='dossie_advogado_rel', 
        column1='dossie_id', 
        column2='advogado_id',
        string=u'Advogado Adverso')
    advogado_adverso_agressor_ids = fields.Many2many(
        comodel_name='res.partner', 
        relation='dossie_advogado_agressor_rel', 
        column1='dossie_id',
        column2='advogado_id',
        string=u'Agressores', 
        compute='get_advogado_adverso_agressor_ids')
    related_advogado_adverso_ids = fields.Many2many(
        string=u'Advogado Adverso Related',
        related='advogado_adverso_ids')
    ########## PARECER ##########

    parecer = fields.Selection(
        selection=parecer_vals,
        string=u'Parecer')
    relatorio_parecer = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Relatório do Parecer')

    ########## TIPO DE CASO ##########

    objeto_id = fields.Many2one(
        comodel_name='dossie.objeto', 
        string=u'Objeto')
    assunto_id = fields.Many2one(
        comodel_name='dossie.assunto', 
        string=u'Assunto')
    natureza_id = fields.Many2one(
        comodel_name='dossie.natureza', 
        string=u'Natureza')
    risco = fields.Selection(
        selection=risco_vals, 
        string=u'Risco')

    ########## VALORES DA CAUSA ##########

    valor_causa = fields.Monetary(
        string=u'Valor da Causa', 
        currency_field='currency_id')
    valor_causa_media = fields.Monetary(
        string=u'Média Valor da Causa', 
        currency_field='currency_id',
        related='valor_causa', 
        group_operator='avg', 
        readonly=True, 
        store=True)
    valor_dano_moral = fields.Monetary(
        string=u'Valor Danos Morais', 
        currency_field='currency_id')
    valor_dano_moral_media = fields.Monetary(
        string=u'Média Valor Danos Morais', 
        currency_field='currency_id',
        related='valor_dano_moral', 
        group_operator='avg', 
        readonly=True, 
        store=True)
    valor_dano_material = fields.Monetary(
        string=u'Valor Danos Materiais', 
        currency_field='currency_id')
    valor_dano_material_media = fields.Monetary(
        string=u'Média Valor Danos Materiais', 
        currency_field='currency_id',
        related='valor_dano_material', 
        group_operator='avg', 
        readonly=True, 
        store=True)

    ########## LOCAL E DATA ##########

    local_fato = fields.Char(
        string=u'Local do Fato')
    data_fato = fields.Date(
        string=u'Data do Fato')
    data_audiencia_inicial = fields.Datetime(
        string=u'Data Audiencia Inicial')
    tipo_acao_id = fields.Many2one(
        comodel_name='dossie.tipo.acao', 
        string=u'Tipo de Ação')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id)

    ########## ACORDO ##########

    analise_acordo = fields.Selection(
        selection=analise_acordo_vals, 
        string=u'Analise de Acordo')
    valor_alcada = fields.Monetary(
        string=u'Valor de Alçada', 
        currency_field='currency_id')
    valor_alcada_media = fields.Monetary(
        string=u'Média Valor de Alçada', 
        currency_field='currency_id',
        related='valor_alcada', 
        group_operator='avg', 
        readonly=True, 
        store=True)
    obrigacao_alcada = fields.Text(
        string=u'Alçada de Obrigação')
    motivo_inaptidao = fields.Many2one(
        comodel_name='motivo.inaptidao', 
        string=u'Motivo da Inaptidao')

    ########## OUTROS ##########

    dossie_id = fields.Many2one(
        comodel_name='dossie.dossie',
        string='Dossiê o Próprio')

    doc_count = fields.Integer(
        compute='_compute_attached_docs_count', 
        string='Número de Documentos Anexados')

    tem_acordo = fields.Boolean(
        string=u'Teve Acordo?')
    tem_dispensa = fields.Boolean(
        string=u'Tem Dispensa?')
    recurso_representada = fields.Boolean(
        string=u'Recurso da Parte Representada?')
    recurso_contraria = fields.Boolean(
        string=u'Recurso da Parte Contrária?')
        

    ########## CITAÇÃO E PENHORA ##########

    data_citacao_efetivada = fields.Date(
        string=u'Data Citação')
    data_penhora_efetivada = fields.Date(
        string=u'Data Penhora')
    relatorio_irrecuperabilidade = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Relatório de Irrecuperabilidade')

    ########## COMPROMISSOS ##########

    task_ids = fields.One2many(
        comodel_name='project.task', 
        inverse_name='dossie_id', 
        string=u'Tarefas')
    user_ids = fields.Many2many(
        comodel_name='res.users', 
        relation='dossie_user_rel', 
        column1='dossie_id', 
        column2='user_id', 
        string=u'Envolvidos',
        compute='_compute_user_ids')

    ########## INICIAL ##########

    inicial = fields.Text(
        related='inicial_id.index_content',
        string=u'Conteúdo da Inicial')
    inicial_id = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Inicial')
    data_distribuicao = fields.Date(
        string=u'Data da Distribuição')

    ########## CITAÇÃO ##########

    citacao = fields.Text(
        related='citacao_id.index_content',
        string=u'Conteúdo da Citação')
    citacao_id = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Citação')
    data_citacao = fields.Date(
        string=u'Data da Citação')

    ########## PEDIDOS ##########

    pedido_ids = fields.One2many(
        comodel_name='dossie.pedido', 
        inverse_name='dossie_id', 
        string=u'Pedidos')

    ########## CITAÇÕES ##########

    citacao_ids = fields.One2many(
        comodel_name='dossie.citacao', 
        inverse_name='dossie_id', 
        string=u'Citações')

    ########## PENHORAS ##########

    penhora_ids = fields.One2many(
        comodel_name='dossie.penhora', 
        inverse_name='dossie_id', 
        string=u'Penhoras')

    ########## DECISÕES ##########

    # LIMINAR
    liminar_id = fields.Many2one(
        comodel_name='dossie.liminar',
        string=u'Liminar')
    liminar = fields.Text(
        store=True,
        related='liminar_id.liminar')
    liminar_anexo_id = fields.Many2one(
        store=True,
        related='liminar_id.anexo_id')
    data_liminar = fields.Date(
        store=True,
        related='liminar_id.data')
    tipos_obrigacoes_ids_liminar = fields.Many2many(
        string=u'Tipos de Obrigação Liminar',
        related='sentenca_id.tipos_obrigacoes_ids')
    tem_multa_obrigacao_liminar = fields.Selection(
        string='Obrigação Tem Multa Liminar',
        related='sentenca_id.tem_multa_obrigacao')
    obrigacao_valor_multa_liminar =  fields.Monetary(
        string=u'Valor da Multa da Obrigação Liminar',
        related='sentenca_id.obrigacao_valor_multa')
    obrigacao_liminar = fields.Text(
        string='Obrigação Liminar',
        related='sentenca_id.obrigacao')


    # SENTENÇA
    sentenca_id = fields.Many2one(
        comodel_name='dossie.sentenca', 
        string=u'Sentença')
    sentenca = fields.Text(
        store=True,
        related='sentenca_id.sentenca')
    sentenca_anexo_id = fields.Many2one(
        store=True, 
        related='sentenca_id.anexo_id')
    data_sentenca = fields.Date(
        store=True,
        string=u'Data da Sentença',
        related='sentenca_id.data')
    tipo_sentenca_id = fields.Many2one(
        store=True,
        related='sentenca_id.tipo_sentenca_id')
    valor_dano_moral_sentenca = fields.Monetary(
        string=u'Valor Danos Morais Sentença', 
        related='sentenca_id.valor_dano_moral')
    valor_dano_material_sentenca = fields.Monetary(
        string=u'Valor Danos Materiais Sentença', 
        related='sentenca_id.valor_dano_material')
    valor_condenacao_base_sentenca = fields.Monetary(
        string=u'Valor Condenação Base Sentença', 
        related='sentenca_id.valor_condenacao_base')
    valor_juros_sentenca = fields.Monetary(
        string=u'Valor Juros Sentença', 
        related='sentenca_id.valor_juros')
    valor_honorarios_sentenca = fields.Monetary(
        string=u'Valor Honorários Sentença', 
        related='sentenca_id.valor_honorarios')
    valor_atualizacao_monetaria_sentenca = fields.Monetary(
        string=u'Valor Atualização Monetária Sentença', 
        related='sentenca_id.valor_atualizacao_monetaria')
    valor_condenacao_final_sentenca = fields.Monetary(
        string=u'Valor Condenação Final Sentença', 
        related='sentenca_id.valor_condenacao_final')
    tipos_obrigacoes_ids_sentenca = fields.Many2many(
        string=u'Tipos de Obrigação Sentença',
        related='sentenca_id.tipos_obrigacoes_ids')
    tem_multa_obrigacao_sentenca = fields.Selection(
        string='Obrigação Tem Multa Sentença',
        related='sentenca_id.tem_multa_obrigacao')
    obrigacao_valor_multa_sentenca =  fields.Monetary(
        string=u'Valor da Multa da Obrigação Sentença',
        related='sentenca_id.obrigacao_valor_multa')
    obrigacao_sentenca = fields.Text(
        string='Obrigação Sentença',
        related='sentenca_id.obrigacao')

    # ACORDÃO
    acordao_id = fields.Many2one(
        comodel_name='dossie.acordao', 
        string=u'Acordão')
    acordao_anexo_id = fields.Many2one(
        store=True,
        string=u'Anexo do Acordão',
        related='acordao_id.anexo_id')
    acordao = fields.Text(
        store=True,
        string=u'Conteúdo do Acordão',
        related='acordao_id.acordao')
    data_acordao = fields.Date(
        store=True,
        string=u'Data do Acordão',
        related='acordao_id.data')
    tipo_acordao_id = fields.Many2one(
        store=True,
        string=u'Tipo do Acordão',
        related='acordao_id.tipo_acordao_id')
    tipo_sentenca_modificada_id = fields.Many2one(
        string=u'Tipo de Sentença Modificada',
        related='acordao_id.tipo_sentenca_modificada_id')
    valor_dano_moral_acordao = fields.Monetary(
        string=u'Valor Danos Morais Acordão', 
        related='acordao_id.valor_dano_moral')
    valor_dano_material_acordao = fields.Monetary(
        string=u'Valor Danos Materiais Acordão', 
        related='acordao_id.valor_dano_material')
    valor_condenacao_base_acordao = fields.Monetary(
        string=u'Valor Condenação Base Acordão', 
        related='acordao_id.valor_condenacao_base')
    valor_juros_acordao = fields.Monetary(
        string=u'Valor Juros Acordão', 
        related='acordao_id.valor_juros')
    valor_honorarios_acordao = fields.Monetary(
        string=u'Valor Honorários Acordão', 
        related='acordao_id.valor_honorarios')
    valor_atualizacao_monetaria_acordao = fields.Monetary(
        string=u'Valor Atualização Monetária Acordão', 
        related='acordao_id.valor_atualizacao_monetaria')
    valor_condenacao_final_acordao = fields.Monetary(
        string=u'Valor Condenação Final Acordão', 
        related='acordao_id.valor_condenacao_final')
    tipos_obrigacoes_ids_acordao = fields.Many2many(
        string=u'Tipos de Obrigação Acordão',
        related='acordao_id.tipos_obrigacoes_ids')
    tem_multa_obrigacao_acordao = fields.Selection(
        string='Obrigação Tem Multa Acordão',
        related='acordao_id.tem_multa_obrigacao')
    obrigacao_valor_multa_acordao =  fields.Monetary(
        string=u'Valor da Multa da Obrigação Acordão',
        related='acordao_id.obrigacao_valor_multa')
    obrigacao_acordao = fields.Text(
        string='Obrigação Acordão',
        related='acordao_id.obrigacao')
         

    # ACORDÃO SUPERIOR
    acordao_superior_id = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Acordão Superior')
    acordao_superior = fields.Text(
        string=u'Conteúdo do Acordão Superior',
        related='acordao_superior_id.index_content')
    data_acordao_superior = fields.Date(
        string=u'Data do Acordão Superior')
    tipo_acordao_superior_id = fields.Many2one(
        comodel_name='tipo.acordao', 
        string=u'Tipo do Acordão Superior')
    
    # ACORDÃO SUPREMO
    acordao_supremo_id = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Acordão Supremo')
    acordao_supremo = fields.Text(
        string=u'Conteúdo do Acordão Supremo',
        related='acordao_supremo_id.index_content')
    data_acordao_supremo = fields.Date(
        string=u'Data do Acordão Supremo')
    tipo_acordao_supremo_id = fields.Many2one(
        comodel_name='tipo.acordao', 
        string=u'Tipo do Acordão Supremo')

    ########## VALORES ##########

    tem_pagamento = fields.Selection(
        selection=[('a', u'Pagamento por Acordo'), ('c', u'Pagamento por Condenação'), ('s', u'Sem Pagamento')], 
        string=u'Tem Pagamento', 
        store=True, 
        compute='_get_tem_pagamento')
    tem_garantia = fields.Selection(
        selection=boolean_selection_vals, 
        string=u'Tem Garantia', 
        compute='_get_tem_pagamento')
    dossie_pagamento_ids = fields.One2many(
        comodel_name='dossie.pagamento', 
        inverse_name='dossie_id', 
        string=u'Valores')
    total_pagamentos = fields.Monetary(
        string=u'Total Pagamentos', 
        currency_field='currency_id',
        compute='_get_total_pagamentos', 
        readonly=True)
    media_pagamentos = fields.Monetary(
        string=u'Média Pagamentos',
        related='total_pagamentos', 
        group_operator='avg', 
        readonly=True, 
        store=True)
    total_custas = fields.Monetary(
        string=u'Total Custas', 
        currency_field='currency_id',
        compute='_get_total_custas', 
        readonly=True)
    media_custas = fields.Monetary(
        string=u'Média Custas',
        related='total_custas', 
        group_operator='avg', 
        readonly=True, 
        store=True)
    total_honorarios = fields.Monetary(
        string=u'Total Honorários', 
        currency_field='currency_id',
        compute='_get_total_honorarios', 
        readonly=True)
    media_honorarios = fields.Monetary(
        string=u'Média Honorários', 
        related='total_honorarios', 
        group_operator='avg', 
        readonly=True, 
        store=True)
    total_dossie = fields.Monetary(
        string=u'Total Processo', 
        currency_field='currency_id',
        compute='_get_total_dossie', 
        readonly=True)
    media_dossie = fields.Monetary(
        string=u'Média Processo', 
        related='total_dossie', 
        group_operator='avg', 
        readonly=True, 
        store=True)

    ########## ALTERAÇÃO DE FASES ##########

    data_encerramento = fields.Date(
        string=u'Data de Encerramento')
    fase_historico_ids = fields.One2many(
        comodel_name='dossie.fase.historico', 
        inverse_name='dossie_id', 
        string=u'Histórico de Fases')
    fase_historico_erro_ids = fields.One2many(
        comodel_name='dossie.fase.historico.erro', 
        inverse_name='dossie_id', 
        string=u'Erro de Histórico de Fases')

    ########## MOVIMENTAÇÕES #########

    movimentacao_historico_ids = fields.One2many(
        comodel_name='dossie.movimentacao', 
        inverse_name='dossie_id', 
        sting=u'Histórico de Movimentações')

    dossie_historico_ids = fields.One2many(
        comodel_name='dossie.dossie', 
        inverse_name='dossie_id', 
        string=u'Histórico de Dossiê', 
        readonly=True)
    analise_historico = fields.Selection(
        selection=analise_historico_state_vals, 
        string=u'Análise do Histórico', 
        readonly=True)
    juiz_grupo_ids = fields.Many2many(
        comodel_name='juiz.grupo.relation', 
        relation='juiz_grupo_relation_rel', 
        column1='dossie_id', 
        column2='juiz_group_id',
        string=u'Juiz Grupo Relations', 
        readonly=True)

    fase_cliente = fields.Char(
        string=u'Fase Cliente')


    @api.one
    @api.depends('dossie_pagamento_ids')
    def _get_tem_pagamento(self):
        for pagamento in self.dossie_pagamento_ids:
            if pagamento.tipo_id.tipo_pagamento == 'g':
                self.tem_garantia = 's'
            else:
                self.tem_garantia = 'n'
        for pagamento in self.dossie_pagamento_ids:
            if pagamento.tipo_id.tipo_pagamento == 'a':
                self.tem_pagamento = 'a'
                break
            if pagamento.tipo_id.tipo_pagamento == 'c':
                self.tem_pagamento = 'c'
                break
        else:
            self.tem_pagamento = 's'

    @api.multi
    def write(self, vals):
        for record in self:
            fase_cliente = False
            if 'fase_id' in vals.keys():
                vals.update(
                    {'fase_id_bkp': record.fase_id and record.fase_id.id or False})
            if vals.get('state') == 'e':
                vals.update({'data_encerramento': fields.Date.today()})

        super(DossieDossie, self).write(vals)

        for record in self:
            for config in self.env['dossie.fase.cliente.config'].search([]):
                rule = expression.normalize_domain(safe_eval(config.dominio))
                dossie = self.env['dossie.dossie'].search(rule)
                if dossie and record.id in dossie.ids:                
                    fase_cliente = config.name
                    break
            vals.update({'fase_cliente': fase_cliente})
        return super(DossieDossie, self).write(vals)

    @api.one
    def _get_total_pagamentos(self):
        self.total_pagamentos = sum(
            [line.valor for line in self.dossie_pagamento_ids if line.tipo_id.tipo == 'p'])

    @api.one
    def _get_total_custas(self):
        self.total_custas = sum(
            [line.valor for line in self.dossie_pagamento_ids if line.tipo_id.tipo == 'c'])

    @api.one
    def _get_total_honorarios(self):
        self.total_honorarios = sum(
            [line.valor for line in self.dossie_pagamento_ids if line.tipo_id.tipo == 'h'])

    @api.one
    def _get_total_dossie(self):
        self.total_dossie = sum(self.dossie_pagamento_ids.mapped('valor'))

    @api.one
    def _get_condenacao_acordao_superior(self):
        self.valor_condenacao_acordao_superior = self.valor_dano_moral_acordao_superior + \
            self.valor_dano_material_acordao_superior

    @api.one
    def _get_condenacao_acordao_supremo(self):
        self.valor_condenacao_acordao_supremo = self.valor_dano_moral_acordao_supremo + \
            self.valor_dano_material_acordao_supremo

    @api.one
    @api.constrains('name')
    def validate_dossie(self):
        if self.name:
            dossies = self.search([('name', '=', self.name)])
            if len(dossies) > 1:
                raise Warning(u'Duplicate Dossiê %s!' % self.name)
        return True

    @api.one
    @api.constrains('processo')
    def validate_processo(self):
        if self.processo:
            dossies = self.search([('processo', '=', self.processo)])
            if len(dossies) > 1:
                raise Warning(u'Duplicate Processo %s!' % self.processo)
        return True

    @api.one
    @api.depends('parte_contraria_ids')
    def get_parte_contraria_contumaz_ids(self):
        self.parte_contraria_contumaz_ids = [
            parte.id for parte in self.parte_contraria_ids if parte.is_contumaz]

    @api.one
    @api.depends('advogado_adverso_ids')
    def get_advogado_adverso_agressor_ids(self):
        self.advogado_adverso_agressor_ids = [
            parte.id for parte in self.advogado_adverso_ids if parte.is_agressor]

    @api.model
    def create(self, vals):
        res = super(DossieDossie, self).create(vals)
        res.dossie_id = res.id
        if res.inicial_id:
            res.inicial_id.res_id = res.id
        if res.citacao_id:
            res.citacao_id.res_id = res.id
        if res.sentenca_id:
            res.sentenca_id.res_id = res.id
        if res.acordao_id:
            res.acordao_id.res_id = res.id
        if res.acordao_superior_id:
            res.acordao_superior_id.res_id = res.id
        if res.acordao_supremo_id:
            res.acordao_supremo_id.res_id = res.id
        return res

    def _compute_user_ids(self):
        users = []
        for dossie in self:
            for task in dossie.task_ids:
                users = users + task.user_ids.ids
            users = list(set(users))
            dossie.user_ids = [(6, 0, users)]

    def count_tasks(self):
        task_ids = self.task_ids.ids
        tree_id = self.env.ref('project.view_task_tree2').id
        form_id = self.env.ref('project.view_task_form2').id
        return {
            'type': 'ir.actions.act_window',
            'name': u'Tarefas',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', task_ids)],
            'res_model': 'project.task',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
        }

    def count_action_lines(self):
        action_lines = []
        tree_id = self.env.ref(
            'tko_project_task_actions.task_action_line_tree_view').id
        form_id = self.env.ref(
            'tko_project_task_actions.task_action_line_form_view').id
        for task in self.task_ids:
            action_lines = action_lines + task.action_line_ids.ids
        return {
            'type': 'ir.actions.act_window',
            'name': u'Ações',
            'view_mode': 'tree',
            'view_type': 'form',
            'domain': [('id', 'in', action_lines)],
            'res_model': 'project.task.action.line',
            'nodestroy': True,
            'views': [(tree_id, 'tree'), (form_id, 'form')],
        }

    def _compute_user_ids(self):
        users = []
        for dossie in self:
            for task in dossie.task_ids:
                users = users + task.user_ids.ids
            users = list(set(users))
            dossie.user_ids = [(6, 0, users)]

    def count_tasks(self):
        task_ids = self.task_ids.ids
        tree_id = self.env.ref('project.view_task_tree2').id
        form_id = self.env.ref('project.view_task_form2').id
        return {
            'type': 'ir.actions.act_window',
            'name': u'Tarefas',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'domain': [('id', 'in', task_ids)],
            'res_model': 'project.task',
            'views': [(tree_id, 'tree'), (form_id, 'form')],
        }

    def count_action_lines(self):
        action_lines = []
        tree_id = self.env.ref(
            'tko_project_task_actions.task_action_line_tree_view').id
        form_id = self.env.ref(
            'tko_project_task_actions.task_action_line_form_view').id
        for task in self.task_ids:
            action_lines = action_lines + task.action_line_ids.ids
        return {
            'type': 'ir.actions.act_window',
            'name': u'Ações',
            'view_mode': 'tree',
            'view_type': 'form',
            'domain': [('id', 'in', action_lines)],
            'res_model': 'project.task.action.line',
            'nodestroy': True,
            'views': [(tree_id, 'tree'), (form_id, 'form')],
        }

    @api.one
    def get_numero_pendencias(self):
        types = self.env['task.type'].search(
            [('name', 'in', [u'Pagamento', u'Obrigação', u'Levantamento'])])
        stages = self.env['project.task.type'].search(
            [('name', 'in', [u'Concluído', u'Cancelado'])])
        tasks = self.env['project.task'].search(
            [('task_type_id', 'in', types.ids), ('dossie_id', '=', self.id), ('stage_id', 'not in', stages.ids)])
        self.numero_pendencias = len(tasks)

    def search_numero_pendencias(self, operator, operand):
        result = []
        for dossie in self.search([]):
            # append 0 in case a single element found
            types = tuple(
                self.env['task.type'].search([('name', 'in', [u'Pagamento', u'Obrigação', u'Levantamento'])]).ids + [0])
            stages = tuple(
                self.env['project.task.type'].search([('name', 'in', [u'Concluído', u'Cancelado'])]).ids + [0])
            query = "select id from project_task where task_type_id in %s and stage_id not in %s and dossie_id = %s" % (
                types, stages, dossie.id)
            self.env.cr.execute(query)
            tasks = self.env.cr.fetchall()
            if operator == '=':
                if len(tasks) == operand:
                    result.append(dossie.id)
            if operator == '>':
                if len(tasks) > operand:
                    result.append(dossie.id)
            if operator == '<':
                if len(tasks) < operand:
                    result.append(dossie.id)
            if operator == '>=':
                if len(tasks) >= operand:
                    result.append(dossie.id)
            if operator == '<=':
                if len(tasks) <= operand:
                    result.append(dossie.id)
            if operator == '!=':
                if len(tasks) != operand:
                    result.append(dossie.id)
        return [('id', 'in', result)]

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for dossie in self:
            dossie.doc_count = Attachment.search_count([
                '|',
                '&',
                ('res_model', '=', 'dossie.dossie'), ('res_id', '=', dossie.id),
                '&',
                ('res_model', '=', 'project.task'), ('res_id',
                                                     'in', dossie.task_ids.ids)
            ])

    def _compute_parte_representada_count(self):
        for dossie in self:
            dossie.parte_representada_count = len(dossie.parte_representada_ids)

    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        attachment_ids = []
        domain = [
            '|', ('id', 'in', attachment_ids),
            '|',
            '&', ('res_model', '=', 'dossie.dossie'), ('res_id', 'in', self.ids),
            '&', ('res_model', '=', 'project.task'), ('res_id', 'in', self.task_ids.ids)]

        task_model = self.env['ir.model'].search(
            [('model', '=', 'project.task')])
        if task_model:
            field_names = self.env['ir.model.fields'].search(
                [('model_id', '=', task_model.id), ('relation', '=', 'ir.attachment'),
                 ('ttype', '=', 'many2one')]).mapped('name')
            for task in self.task_ids:
                for field_name in field_names:
                    attachment = getattr(task, field_name)
                    if attachment:
                        attachment_ids.append(attachment.id)

        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                                    Documents are attached to the tasks and issues of your project.</p><p>
                                    Send messages or log internal notes with attachments to link
                                    documents to your project.
                                </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    @api.multi
    def create_new_task(self):
        return {
            'name': _('Task'),
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            'context': "{'default_dossie_id': %s}" % (self.id)
        }

    def _cron_dossie_task(self):
        _logger.info(u'Starting cron job on Dossie - Dossie...')
        dossies = self.search([])
        for dossie in dossies:
            dossie_ids = self.search([('id', '!=', dossie.id),
                                      ('parte_contraria_ids.id', 'in', [parte.id for parte in dossie.parte_contraria_ids])])

            dossie_ids_a = dossie_ids.search(
                [('id', 'in', dossie_ids.ids), ('state', '=', 'a')]).ids
            dossie_ids_e = dossie_ids.search(
                [('id', 'in', dossie_ids.ids), ('state', '=', 'e')]).ids

            juiz_grupo_ids = self.env['juiz.grupo.relation'].search(
                [('juiz_id', '=', dossie.juiz_id.id)])

            analise_historico_state = 'slcj'
            dossie_a_count = len(dossie_ids_a)
            dossie_e_count = len(dossie_ids_e)
            if dossie_a_count <= 0 and dossie_e_count <= 0:
                analise_historico_state = 'slcj'
            elif dossie_a_count > 0 and dossie_e_count <= 0:
                analise_historico_state = 'pl'
            elif dossie_a_count <= 0 and dossie_e_count > 0:
                analise_historico_state = 'pcj'
            elif dossie_a_count > 0 and dossie_e_count > 0:
                analise_historico_state = 'plcj'
            dossie.write({'analise_historico': analise_historico_state, 'dossie_historico_ids': [(6, 0, dossie_ids.ids)],
                          'juiz_grupo_ids': [(6, 0, juiz_grupo_ids.ids)]})
        _logger.info(u'Ending cron job on Dossie - Dossie...')
        return

########## OUTROS ##########
# pl = >=1 dossie in dossie_historico_ids in state = a & 0 dossie in dossie_historico_ids state = e
# cj =  >=1 dossie in dossie_historico_ids in state = e & 0 dossie in dossie_historico_ids state = a
# plcj =  >=1 dossie in dossie_historico_ids in state = a & >=1 dossie in
# dossie_historico_ids state = e


class MotivoInaptidao(models.Model):
    _name = 'motivo.inaptidao'
    _description = u'Motivo de Inaptidão'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class DossieAssunto(models.Model):
    _name = 'dossie.assunto'
    _description = u'Assunto'

    name = fields.Char(
        string=u'Nome', 
        required=True)
    objeto_ids = fields.Many2many(
        comodel_name='dossie.objeto', 
        relation='assunto_objeto_rel', 
        column1='assunto_id', 
        column2='objeto_id', 
        string=u'Objetos')
    grupo_id = fields.Many2one(
        comodel_name='res.partner', 
        string=u'Grupo',
        domain=[('is_grupo','=',True)])


class DossieObjeto(models.Model):
    _name = 'dossie.objeto'
    _description = u'Objeto'

    name = fields.Char(
        string=u'Nome', 
        required=True)
    grupo_id = fields.Many2one(
        comodel_name='res.partner', 
        string=u'Grupo',
        domain=[('is_grupo','=',True)])


class DossieVara(models.Model):
    _name = 'dossie.vara'
    _description = u'Vara'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class DossieOrgao(models.Model):
    _name = 'dossie.orgao'
    _description = u'Orgão'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class DossieRito(models.Model):
    _name = 'dossie.rito'
    _description = u'Rito'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class DossieCarteira(models.Model):
    _name = 'dossie.carteira'
    _description = u'Carteira'

    name = fields.Char(
        string=u'Nome', 
        required=True)
    data_de_corte = fields.Date(
        string=u'Data de Corte')


class DossieFase(models.Model):
    _name = 'dossie.fase'
    _description = u'Fase'

    name = fields.Char(
        string=u'Nome', required=True)
    peso = fields.Integer(
        string=u'Peso')
    polo_cliente = fields.Selection(
        selection=polo_cliente_vals,
        string=u'Polo Cliente',
        required=True)


class DossieOrigem(models.Model):
    _name = 'dossie.origem'
    _description = u'Origem'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class DossieNatureza(models.Model):
    _name = 'dossie.natureza'
    _description = u'Natureza'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class DossieTipoAcao(models.Model):
    _name = 'dossie.tipo.acao'
    _description = u'Tipo de Ação'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class DossieMotivoCadastro(models.Model):
    _name = 'dossie.motivo.cadastro'
    _description = u'Motivo de Cadastro'

    name = fields.Char(
        string=u'Nome', 
        required=True)


########## LIMINAR ##########


class DossieLiminar(models.Model):
    _name = 'dossie.liminar'
    _description = u'Liminar'

    dossie_id = fields.Many2one(
        comodel_name='dossie.dossie', 
        string=u'Dossiê')

    name = fields.Char(
        string=u'Nome', 
        compute='get_liminar_name', 
        readonly='1')
    
    data = fields.Date(
        string=u'Data')
    anexo_id = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Anexo Liminar')
    liminar = fields.Text(
        string=u'Conteúdo da Liminar',
        related='anexo_id.index_content')
    tipo_liminar_id = fields.Many2one(
        comodel_name='tipo.liminar', 
        string=u'Tipo de Liminar')
    tipos_obrigacoes_ids = fields.Many2many(
        comodel_name='tipo.obrigacao',
        relation='tipos_obrigacoes_sentenca_rel',
        column1='sentenca_id',
        column2='tipo_id',
        string=u'Tipos de Obrigação')
    tem_multa_obrigacao = fields.Selection(
        selection=multa_selection_vals,
        string='Obrigação Tem Multa')
    obrigacao_valor_multa =  fields.Monetary(
        string=u'Valor da Multa da Obrigação', 
        currency_id='currency_id',)
    obrigacao = fields.Text(
        string='Obrigação')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    
    # ADDITIONS
    
    processo = fields.Char(
        related='dossie_id.processo', 
        store=True)
    objeto_id = fields.Many2one( 
        related='dossie_id.objeto_id', 
        store=True)
    assunto_id = fields.Many2one(
        related='dossie_id.assunto_id', 
        store=True)
    estado_id = fields.Many2one(
        related='dossie_id.estado_id', 
        store=True)
    comarca_id = fields.Many2one(
        related='dossie_id.comarca_id', 
        store=True)
    orgao_id = fields.Many2one(
        related='dossie_id.orgao_id', 
        store=True)
    vara_id = fields.Many2one(
        related='dossie_id.vara_id', 
        store=True)
    ordinal = fields.Integer(
        related='dossie_id.ordinal', 
        store=True)
    grupo_id = fields.Many2one(
        related='dossie_id.grupo_id', 
        store=True)

    @api.one
    @api.depends('tipo_liminar_id', 'processo')
    def get_liminar_name(self):
        name = self.tipo_liminar_id.name or ' '
        if self.dossie_id:
            name = self.processo + ' | ' + name
        self.name = name

########## Sentenca ##########


class DossieSentenca(models.Model):
    _name = 'dossie.sentenca'
    _description = u'Sentença'

    dossie_id = fields.Many2one(
        comodel_name='dossie.dossie', 
        string=u'Dossiê')

    name = fields.Char(
        string=u'Nome', 
        compute='get_sentenca_name', 
        readonly='1')
    
    data = fields.Date(
        string=u'Data')
    anexo_id = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Anexo Sentença')
    sentenca = fields.Text(
        string=u'Conteúdo da Sentença',
        related='anexo_id.index_content')
    tipo_sentenca_id = fields.Many2one(
        comodel_name='tipo.sentenca',
        string=u'Tipo de Sentença')

    tipo_condenacao = fields.Selection(
        selection=tipo_condenacao_vals,
        string=u'Tipo de Condenação')
    juiz_id = fields.Many2one(
        comodel_name='res.partner', 
        string=u'Juiz')
    fundamento_id = fields.Many2one(
        comodel_name='dossie.sentenca.fundamento', 
        string=u'Fundamento')
    tipo_materia_id = fields.Many2one(
        comodel_name='dossie.sentenca.materia', 
        string=u'Matéria')
    
    valor_dano_moral = fields.Monetary(
        string=u'Valor Danos Morais', 
        currency_field='currency_id')
    valor_dano_moral_media = fields.Monetary(
        string=u'Média Valor Danos Morais',
        related='valor_dano_moral', 
        group_operator='avg',
        readonly=True, 
        store=True)
    valor_dano_material = fields.Monetary(
        string=u'Valor Danos Materiais', 
        currency_field='currency_id')
    valor_dano_material_media = fields.Monetary(
        string=u'Média Valor Danos Materiais',
        related='valor_dano_material', 
        group_operator='avg',
        readonly=True, 
        store=True)
    valor_condenacao_base = fields.Monetary(
        string=u'Valor Condenação Base', 
        currency_id='currency_id',
        compute='_get_condenacao_sentenca_base')
    valor_condenacao_media = fields.Monetary(
        string=u'Média Valor Condenação',
        related='valor_condenacao_base', 
        group_operator='avg',
        readonly=True, 
        store=True)
    valor_juros = fields.Monetary(
        string=u'Valor Juros', 
        currency_id='currency_id')
    valor_juros_media = fields.Monetary(
        string=u'Média Valor Juros',
        related='valor_juros', 
        group_operator='avg',
        readonly=True, 
        store=True)
    valor_honorarios = fields.Monetary(
        string=u'Valor Honorários', 
        currency_id='currency_id')
    valor_honorarios_media = fields.Monetary(
        string=u'Média Valor Honorários',
        related='valor_honorarios', 
        group_operator='avg',
        readonly=True, 
        store=True)
    valor_atualizacao_monetaria = fields.Monetary(
        string=u'Valor Atualização Monetária', 
        currency_id='currency_id')
    valor_atualizacao_monetaria_media = fields.Monetary(
        string=u'Média Valor Atualização Monetária',
        related='valor_atualizacao_monetaria', 
        group_operator='avg',
        readonly=True, 
        store=True)
    valor_condenacao_final = fields.Monetary(
        string=u'Valor Condenação Final', 
        currency_id='currency_id',
        compute='_get_condenacao_sentenca_final')
    valor_condenacao_final_media = fields.Monetary(
        string=u'Média Valor Condenação Final',
        related='valor_condenacao_final', 
        group_operator='avg',
        readonly=True, 
        store=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    
    tipos_obrigacoes_ids = fields.Many2many(
        comodel_name='tipo.obrigacao',
        relation='tipos_obrigacoes_sentenca_rel',
        column1='sentenca_id',
        column2='tipo_id',
        string=u'Tipos de Obrigação')
    tem_multa_obrigacao = fields.Selection(
        selection=multa_selection_vals,
        string='Obrigação Tem Multa')
    obrigacao_valor_multa =  fields.Monetary(
        string=u'Valor da Multa da Obrigação', 
        currency_id='currency_id')
    obrigacao = fields.Text(
        string='Obrigação')
    
    # ADDITIONS
    
    processo = fields.Char(
        related='dossie_id.processo', 
        store=True)
    objeto_id = fields.Many2one( 
        related='dossie_id.objeto_id', 
        store=True)
    assunto_id = fields.Many2one(
        related='dossie_id.assunto_id', 
        store=True)
    estado_id = fields.Many2one(
        related='dossie_id.estado_id', 
        store=True)
    comarca_id = fields.Many2one(
        related='dossie_id.comarca_id', 
        store=True)
    orgao_id = fields.Many2one(
        related='dossie_id.orgao_id', 
        store=True)
    vara_id = fields.Many2one(
        related='dossie_id.vara_id', 
        store=True)
    ordinal = fields.Integer(
        related='dossie_id.ordinal', 
        store=True)
    grupo_id = fields.Many2one(
        related='dossie_id.grupo_id', 
        store=True)
    juiz_grupo_id = fields.Many2one(
        comodel_name='juiz.grupo.relation', 
        string=u'Estudo de Decisões')

    @api.one
    @api.depends('tipo_sentenca_id', 'processo')
    def get_sentenca_name(self):
        name = self.tipo_sentenca_id.name or ' '
        if self.dossie_id:
            name = self.processo + ' | ' + name
        self.name = name

    @api.one
    @api.depends('valor_dano_moral', 'valor_dano_material')
    def _get_condenacao_sentenca_base(self):
        self.valor_condenacao_base = self.valor_dano_moral + self.valor_dano_material

    @api.depends('valor_dano_moral', 'valor_dano_material', 'valor_juros', 'valor_atualizacao_monetaria', 'valor_honorarios')
    def _get_condenacao_sentenca_final(self):
        self.valor_condenacao_final = self.valor_dano_moral + self.valor_dano_material + self.valor_juros + self.valor_atualizacao_monetaria + self.valor_honorarios


class DossieSentencaMateria(models.Model):
    _name = 'dossie.sentenca.materia'
    _description = u'Matéria da Sentença'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class DossieSentencaFundamento(models.Model):
    _name = 'dossie.sentenca.fundamento'
    _description = u'Fundamento da Sentença'

    name = fields.Char(
        string=u'Nome', 
        required=True)

########## ACORDÃO ##########

class DossieAcordao(models.Model):
    _name = 'dossie.acordao'
    _description = u'Acordão'

    dossie_id = fields.Many2one(
        comodel_name='dossie.dossie', 
        string=u'Dossiê')

    name = fields.Char(
        string=u'Nome', 
        compute='get_acordao_name', 
        readonly='1')
    
    data = fields.Date(
        string=u'Data')
    anexo_id = fields.Many2one(
        comodel_name='ir.attachment', 
        string=u'Anexo Acordão')
    acordao = fields.Text(
        string=u'Conteúdo do Acordão',
        related='anexo_id.index_content')
    tipo_acordao_id = fields.Many2one(
        comodel_name='tipo.acordao', 
        string=u'Tipo de Liminar')
    sentenca_id = fields.Many2one(
        comodel_name='dossie.sentenca',
        string=u'Sentença')
    tipo_sentenca_modificada_id = fields.Many2one(
        comodel_name='tipo.sentenca',
        string=u'Tipo de Sentença Modificada')
    valor_dano_moral = fields.Monetary(
        string=u'Valor Danos Morais', 
        currency_field='currency_id')
    valor_dano_moral_media = fields.Monetary(
        string=u'Média Valor Danos Morais',
        related='valor_dano_moral', 
        group_operator='avg',
        readonly=True, 
        store=True)
    valor_dano_material = fields.Monetary(
        string=u'Valor Danos Materiais', 
        currency_field='currency_id')
    valor_dano_material_media = fields.Monetary(
        string=u'Média Valor Danos Materiais',
        related='valor_dano_material', 
        group_operator='avg',
        readonly=True, 
        store=True)
    valor_condenacao_base = fields.Monetary(
        string=u'Valor Condenação Base', 
        currency_id='currency_id')
    valor_condenacao_media = fields.Monetary(
        string=u'Média Valor Condenação',
        related='valor_condenacao_base', 
        group_operator='avg',
        readonly=True, 
        store=True)
    valor_juros = fields.Monetary(
        string=u'Valor Juros', 
        currency_id='currency_id')
    valor_juros_media = fields.Monetary(
        string=u'Média Valor Juros',
        related='valor_juros', 
        group_operator='avg',
        readonly=True, 
        store=True)
    valor_honorarios = fields.Monetary(
        string=u'Valor Honorários', 
        currency_id='currency_id')
    valor_honorarios_media = fields.Monetary(
        string=u'Média Valor Honorários',
        related='valor_honorarios', 
        group_operator='avg',
        readonly=True, 
        store=True)
    valor_atualizacao_monetaria = fields.Monetary(
        string=u'Valor Atualização Monetária', 
        currency_id='currency_id')
    valor_atualizacao_monetaria_media = fields.Monetary(
        string=u'Média Valor Atualização Monetária',
        related='valor_atualizacao_monetaria', 
        group_operator='avg',
        readonly=True, 
        store=True)
    valor_condenacao_final = fields.Monetary(
        string=u'Valor Condenação Final', 
        currency_id='currency_id')
    valor_condenacao_final_media = fields.Monetary(
        string=u'Média Valor Condenação Final',
        related='valor_condenacao_final', 
        group_operator='avg',
        readonly=True, 
        store=True)
    tipos_obrigacoes_ids = fields.Many2many(
        comodel_name='tipo.obrigacao',
        relation='tipos_obrigacoes_sentenca_rel',
        column1='sentenca_id',
        column2='tipo_id',
        string=u'Tipos de Obrigação')
    tem_multa_obrigacao = fields.Selection(
        selection=multa_selection_vals,
        string='Obrigação Tem Multa')
    obrigacao_valor_multa =  fields.Monetary(
        string=u'Valor da Multa da Obrigação', 
        currency_id='currency_id',)
    obrigacao = fields.Text(
        string='Obrigação')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    
    # ADDITIONS
    
    processo = fields.Char(
        related='dossie_id.processo', 
        store=True)
    objeto_id = fields.Many2one( 
        related='dossie_id.objeto_id', 
        store=True)
    assunto_id = fields.Many2one(
        related='dossie_id.assunto_id', 
        store=True)
    estado_id = fields.Many2one(
        related='dossie_id.estado_id', 
        store=True)
    comarca_id = fields.Many2one(
        related='dossie_id.comarca_id', 
        store=True)
    orgao_id = fields.Many2one(
        related='dossie_id.orgao_id', 
        store=True)
    vara_id = fields.Many2one(
        related='dossie_id.vara_id', 
        store=True)
    ordinal = fields.Integer(
        related='dossie_id.ordinal', 
        store=True)
    grupo_id = fields.Many2one(
        related='dossie_id.grupo_id', 
        store=True)

    @api.one
    @api.depends('tipo_acordao_id', 'processo')
    def get_acordao_name(self):
        name = self.tipo_acordao_id.name or ' '
        if self.dossie_id:
            name = self.processo + ' | ' + name
        self.name = name

    @api.one
    @api.depends('valor_dano_moral', 'valor_dano_material')
    def _get_condenacao_acordao_base(self):
        self.valor_condenacao_base = self.valor_dano_moral + \
            self.valor_dano_material

    @api.depends('valor_dano_moral', 'valor_dano_material', 'valor_juros', 'valor_atualizacao_monetaria', 'valor_honorarios')
    def _get_condenacao_acordao_final(self):
        self.valor_condenacao_final = self.valor_dano_moral + self.valor_dano_material + self.valor_juros + self.valor_atualizacao_monetaria + self.valor_honorarios


########## CONTRATO ##########

class DossieContratoCanal(models.Model):
    _name = 'dossie.contrato.canal'
    _description = u'Canal de Contratação'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class DossieContratoModalidade(models.Model):
    _name = 'dossie.contrato.modalidade'
    _description = u'Modalidade de Pagamento'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class DossieContratoSegmento(models.Model):
    _name = 'dossie.contrato.segmento'
    _description = u'Segmento'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class DossieContratoTipo(models.Model):
    _name = 'dossie.contrato.tipo'
    _description = u'Tipo de Contrato'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class DossieContratoParcela(models.Model):
    _name = 'dossie.contrato.parcela'
    _description = u'Parcela'

    name = fields.Char(
        string=u'Nome')
    numero = fields.Integer(
        string=u'Nº',
        required=True)
    valor = fields.Monetary(
        string=u'Valor', 
        currency_field='currency_id',
        required=True)
    valor_media = fields.Monetary(
        string=u'Média Valor', 
        currency_field='currency_id',
        related='valor', 
        group_operator='avg', 
        readonly=True, 
        store=True)
    valor_em_ser = fields.Monetary(
        string=u'Valor "em ser"', 
        currency_field='currency_id')
    valor_em_ser_media = fields.Monetary(
        string=u'Média Valor "em ser"', 
        currency_field='currency_id',
        related='valor_pago', 
        group_operator='avg', 
        readonly=True, 
        store=True)
    valor_ca6 = fields.Monetary(
        string=u'Valor CA 6', 
        currency_field='currency_id')
    valor_ca6_media = fields.Monetary(
        string=u'Média Valor CA6', 
        currency_field='currency_id',
        related='valor_ca6', 
        group_operator='avg', 
        readonly=True, 
        store=True)
    valor_pago = fields.Monetary(
        string=u'Valor Pago', 
        currency_field='currency_id')
    valor_pago_media = fields.Monetary(
        string=u'Média Valor Pago', 
        currency_field='currency_id',
        related='valor_pago', 
        group_operator='avg', 
        readonly=True, 
        store=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency', 
        required=True, 
        default=lambda self: self.env.user.company_id.currency_id)
    data_vencimento = fields.Date(
        string=u'Data de Vencimento')
    situacao = fields.Selection(
        selection=[('a', u'Aberto'), ('l', u'Liquidado'), ('lp', u'Liquidado com Prejuízo')],
        default='a',
        string='Situação')
    data_situacao = fields.Date(
        string=u'Data da Situação')
    contrato_id = fields.Many2one(
        comodel_name='dossie.contrato', 
        string=u'Contrato', 
        required=True,
        ondelete='cascade',)
    dossie_id = fields.Many2one(
        related='contrato_id.dossie_id', 
        readonly=True, 
        store=True,
        ondelete='cascade')


class DossieContratoGarantiaTipo(models.Model):
    _name = 'dossie.contrato.garantia.tipo'
    _description = u'Tipo de Garantia'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class DossieContratoGarantia(models.Model):
    _name = 'dossie.contrato.garantia'
    _description = u'Garantia'

    name = fields.Char(
        string=u'Nome')
    tipo_id = fields.Many2one(
        comodel_name='dossie.contrato.garantia.tipo',
        string='Tipo',
        required=True)
    bem_id = fields.Many2one(
        comodel_name='res.partner.asset', 
        string=u'Bem')
    partner_id = fields.Many2one(
        related='bem_id.partner_id',
        string=u'Parceiro',
        store=True)
    contrato_id = fields.Many2one(
        comodel_name='dossie.contrato', 
        string=u'Contrato', 
        required=True,
        ondelete='cascade')
    dossie_id = fields.Many2one(
        related='contrato_id.dossie_id', 
        readonly=True, 
        store=True,
        ondelete='cascade')


class DossieContrato(models.Model):
    _name = 'dossie.contrato'
    _description = u'Contrato'

    name = fields.Char(
        string=u'Nº', 
        required=True)
    cliente_ids = fields.Many2many(
        comodel_name='res.partner', 
        relation='contrato_cliente_rel', 
        column1='contrato_id', 
        column2='cliente_id', 
        string=u'Clientes',
        required=True)
    avalista_ids = fields.Many2many(
        comodel_name='res.partner', 
        relation='contrato_avalista_rel', 
        column1='contrato_id', 
        column2='avalista_id', 
        string=u'Avalistas')
    tipo_id = fields.Many2one(
        comodel_name='dossie.contrato.tipo', 
        string=u'Tipo', 
        required=True)
    data_inicial = fields.Date(
        string=u'Data Inicial')
    data_atraso = fields.Date(
        string=u'Data do 1º Atraso')
    data_vencimento = fields.Date(
        string=u'Data de Vencimento')
    valor_ca6 = fields.Monetary(
        string=u'Valor CA 6', 
        currency_field='currency_id')
    valor_ca6_media = fields.Monetary(
        string=u'Média Valor CA 6', 
        related='valor_ca6', 
        group_operator='avg', 
        readonly=True, 
        store=True)
    valor_nb = fields.Monetary(
        string=u'Valor NB', 
        currency_field='currency_id')
    valor_nb_media = fields.Monetary(
        string=u'Média Valor NB', 
        related='valor_nb', 
        group_operator='avg', 
        readonly=True, 
        store=True)
    valor_atrasado = fields.Monetary(
        string=u'Valor Atrasado', 
        currency_field='currency_id')
    valor_atrasado_media = fields.Monetary(
        string=u'Média Atrasado', 
        related='valor_atrasado', 
        group_operator='avg', 
        readonly=True, 
        store=True)
    valor_em_ser = fields.Monetary(
        string=u'Valor "em ser"', 
        currency_field='currency_id')
    valor_em_ser_media = fields.Monetary(
        string=u'Média Valor "em ser"', 
        related='valor_em_ser', 
        group_operator='avg', 
        readonly=True, 
        store=True)
    valor_contratado = fields.Monetary(
        string=u'Valor Contratado', 
        currency_field='currency_id')
    valor_contratado_media = fields.Monetary(
        string=u'Média Valor Contratado', 
        related='valor_contratado', 
        group_operator='avg', 
        readonly=True, 
        store=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency', 
        required=True, 
        default=lambda self: self.env.user.company_id.currency_id)
    valor_juros = fields.Float(
        string=u'Juros')
    agencia = fields.Char(
        string=u'Nome da Agência')
    conta_id = fields.Many2one(
        comodel_name='res.partner.bank', 
        string=u'Conta')
    canal_contratacao = fields.Many2one(
        comodel_name='dossie.contrato.canal', 
        string=u'Canal de Contratação')
    modalidade = fields.Many2one(
        comodel_name='dossie.contrato.modalidade', 
        string=u'Modalidade de Pagamento')
    situacao = fields.Selection(
        selection=[('a', u'Aberto'), ('l', 'Liquidado'), ('lp', 'Liquidado com Prejuízo')],
        default='a',
        string=u'Situação')
    data_situacao = fields.Date(
        string=u'Data da Situação')
    documento_ids = fields.Many2many(
        comodel_name='ir.attachment',  
        relation='contrato_attachment_doc_rel', 
        column1='contrato_id',
        column2='attachment_id',
        string=u'Documentos')
    dossie_id = fields.Many2one(
        comodel_name='dossie.dossie', 
        string=u'Dossiê',
        ondelete='cascade')
    parte_contraria_ids = fields.Many2many(
        related='dossie_id.parte_contraria_ids',
        string='Related Parte Contraria')
    segmento_id = fields.Many2one(
        comodel_name='dossie.contrato.segmento', 
        string=u'Segmento')
    parcela_ids = fields.One2many(
        comodel_name='dossie.contrato.parcela', 
        inverse_name='contrato_id', 
        string=u'Parcelas')
    numero_parcelas = fields.Integer(
        string=u'Nº Parcelas')
    garantia_ids = fields.One2many(
        comodel_name='dossie.contrato.garantia', 
        inverse_name='contrato_id', 
        string=u'Garantias')


########## VALORES ##########


class DossieTipoPagamento(models.Model):
    _name = 'dossie.tipo.pagamento'
    _description = u'Tipo de Pagamento'

    name = fields.Char(
        string=u'Nome', 
        required=True)
    tipo = fields.Selection(
        string=u'Tipo Interno',
        selection=dossie_tipo_pagamento_vals, 
        required=True)
    tipo_pagamento = fields.Selection(
        selection=[('a', u'Acordo'), ('g', u'Garantia'), ('c', u'Condenação')],
        string=u'Tipo de Pagamento')


class DossiePagamentoLine(models.Model):
    _name = 'dossie.pagamento'
    _description = u'Motivo de Cadastro'

    valor = fields.Monetary(
        string=u'Valor', 
        currency_field='currency_id')
    valor_media = fields.Monetary(
        string=u'Média Valor',
        related='valor', 
        group_operator='avg',
        readonly=True, 
        store=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    tipo_id = fields.Many2one(
        comodel_name='dossie.tipo.pagamento', 
        string=u'Tipo', 
        required=True)
    data = fields.Date(
        string=u'Data')
    dossie_id = fields.Many2one(
        comodel_name='dossie.dossie', 
        string=u'Dossie')


class JuizGrupoRelation(models.Model):
    _name = 'juiz.grupo.relation'
    _description = u'Estudo de Decisões'

    sentenca_ids = fields.One2many(
        comodel_name='dossie.sentenca', 
        inverse_name='juiz_grupo_id', 
        string=u'Sentenças', 
        readonly=True)
    juiz_id = fields.Many2one(
        comodel_name='res.partner', 
        string=u'Juiz', 
        domain=[('is_juiz', '=', True)])
    dossie_id = fields.Many2one(
        comodel_name='dossie.dossie', 
        string=u'Dossie', 
        readonly=True)
    grupo_id = fields.Many2one(
        comodel_name='res.partner', 
        string=u'Grupo', domain=[('is_grupo', '=', True)])
    improcedencia_total = fields.Integer(
        string=u'Total de Improcedência', 
        readonly=True)
    improcedencia_porcentage = fields.Float(
        string=u'Porcentagem de Improcedência', 
        readonly=True)
    procedencia_total = fields.Integer(
        string=u'Total de Procedência', 
        readonly=True)
    procedencia_porcentage = fields.Float(
        string=u'Porcentagem de Procedência', 
        readonly=True)
    procedencia_danos_morais_media = fields.Float(
        string=u'Média de Danos Morais', 
        readonly=True)
    procedencia_danos_materiais_media = fields.Float(
        string=u'Média de Danos Materiais', 
        readonly=True)
    sentenca_total = fields.Integer(
        string=u'Total de Sentenças', 
        readonly=True)

    def _cron_juiz_grupo_relation_task(self):
        _logger.info(
            u'Starting cron job on Estudo de Decisões - JuizGrupoRelation..')
        juiz_grupos = self.search([])
        for juiz_grupo in juiz_grupos:
            sentenca_ids = self.env['dossie.sentenca'].search(
                [('juiz_id', '=', juiz_grupo.juiz_id.id), ('grupo_id', '=', juiz_grupo.grupo_id.id)])

            _logger.info(sentenca_ids)
            _logger.info(juiz_grupo.juiz_id)
            _logger.info(juiz_grupo.grupo_id)

            sentenca_ids_improcedencia = sentenca_ids.search(
                [('id', 'in', sentenca_ids.ids), ('tipo_sentenca_id.tipo', '=', 'i')]).ids
            sentenca_ids_procedencia = sentenca_ids.search(
                [('id', 'in', sentenca_ids.ids), ('tipo_sentenca_id.tipo', '=', 'p')]).ids
            sentenca_ids_danos_morais = sentenca_ids.search([('id', 'in', sentenca_ids.ids), (
                'tipo_sentenca_id.tipo', '=', 'p'), ('valor_dano_moral_sentenca', '>', 0)])
            sentenca_ids_danos_materiais = sentenca_ids.search([('id', 'in', sentenca_ids.ids), (
                'tipo_sentenca_id.tipo', '=', 'p'), ('valor_dano_material_sentenca', '>', 0)])

            improcedencia_total = improcedencia_porcentage = 0
            procedencia_total = procedencia_porcentage = 0
            procedencia_danos_morais_media = procedencia_danos_materiais_media = 0
            sentenca_total = sum_danos_morais = sum_danos_materiais = 0

            if sentenca_ids.ids:
                sentenca_total = len(sentenca_ids.ids)
                if sentenca_ids_improcedencia:
                    improcedencia_total = len(sentenca_ids_improcedencia)
                    improcedencia_porcentage = 100 * \
                        improcedencia_total / len(sentenca_ids.ids)

                if sentenca_ids_procedencia:
                    procedencia_total = len(sentenca_ids_procedencia)
                    procedencia_porcentage = 100 * \
                        procedencia_total / len(sentenca_ids.ids)

                if sentenca_ids_danos_morais:
                    sum_danos_morais = sum(
                        sentenca.valor_dano_moral_sentenca for sentenca in sentenca_ids_danos_morais)
                    procedencia_danos_morais_media = sum_danos_morais / \
                        len(sentenca_ids_danos_morais.ids)

                if sentenca_ids_danos_materiais:
                    sum_danos_materiais = sum(
                        sentenca.valor_dano_material_sentenca for sentenca in sentenca_ids_danos_materiais)
                    procedencia_danos_materiais_media = sum_danos_materiais / \
                        len(sentenca_ids_danos_materiais.ids)

            juiz_grupo.write({'sentenca_ids': [(6, 0, sentenca_ids.ids)],
                              'improcedencia_total': improcedencia_total, 'improcedencia_porcentage': improcedencia_porcentage,
                              'procedencia_total': procedencia_total, 'procedencia_porcentage': procedencia_porcentage,
                              'procedencia_danos_morais_media': procedencia_danos_morais_media,
                              'procedencia_danos_materiais_media': procedencia_danos_materiais_media,
                              'sentenca_total': sentenca_total})

        _logger.info(
            u'Ending cron job on Estudo de Decisões - JuizGrupoRelation...')
        return

########## MOVIMENTAÇÃO ##########


class TipoAcordao(models.Model):
    _name = 'tipo.acordao'
    _description = u'Tipo de Acordão'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class TipoLiminar(models.Model):
    _name = 'tipo.liminar'
    _description = u'Tipo de Liminar'

    name = fields.Char(
        string=u'Nome',
        required=True)


class TipoSentenca(models.Model):
    _name = 'tipo.sentenca'
    _description = u'Tipo de Sentença'

    name = fields.Char(
        string=u'Nome', 
        required=True)
    tipo = fields.Selection(
        selection=[('i', u'Improcedente'), ('p', u'Procedente')], 
        string=u'Tipo Interno')


class TipoLevantamento(models.Model):
    _name = 'tipo.levantamento'
    _description = u'Tipo de Levantamento'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class TipoAudiencia(models.Model):
    _name = 'tipo.audiencia'
    _description = u'Tipo de Audiência'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class TipoTransito(models.Model):
    _name = 'tipo.transito'
    _description = u'Tipo de Trânsito'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class TipoRecurso(models.Model):
    _name = 'tipo.recurso'
    _description = u'Tipo de Recurso'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class TipoPrazo(models.Model):
    _name = 'tipo.prazo'
    _description = u'Tipo de Prazo'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class TipoEncerramento(models.Model):
    _name = 'tipo.encerramento'
    _description = u'Tipo de Encerramento'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class TipoPagamento(models.Model):
    _name = 'tipo.pagamento'
    _description = u'Tipo de Pagamento'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class TipoObrigacao(models.Model):
    _name = 'tipo.obrigacao'
    _description = u'Tipo de Obrigação'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class TipoDocumento(models.Model):
    _name = 'tipo.documento'
    _description = u'Tipo de Documento'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class DossieMovimentacaoTipo(models.Model):
    _name = 'dossie.movimentacao.tipo'
    _description = u'Tipo de Movimentação'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class DossieMovimentacao(models.Model):
    _name = 'dossie.movimentacao'
    _description = u'Movimentação'

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active

    @api.multi
    def toggle_lido(self):
        for record in self:
            record.lido = not record.lido

    active = fields.Boolean(
        string='Active', 
        default='t')
    resultado = fields.Selection(
        string=u'Resultado', 
        selection=dossie_movimentacao_resultado_vals)
    tipo = fields.Selection(
        string=u'Tipo', 
        selection=dossie_movimentacao_tipo_vals)
    data = fields.Date(
        string=u'Data da Movimentação')
    movimentacao = fields.Text(
        string=u'Movimentação')
    dossie_id = fields.Many2one(
        comodel_name='dossie.dossie', 
        string=u'Dossiê')
    fase_id = fields.Many2one(
        comodel_name='dossie.fase', 
        string=u'Fase Atual', 
        related='dossie_id.fase_id', 
        store=True)
    grupo_id = fields.Many2one(
        comodel_name='res.partner', 
        string=u'Grupo', 
        related='dossie_id.grupo_id', 
        store=True)
    polo_cliente = fields.Selection(
        selection=polo_cliente_vals, 
        string=u'Polo do Cliente', 
        related='dossie_id.polo_cliente', store=True)
    tipo_movimentacao_id = fields.Many2one(
        comodel_name='dossie.movimentacao.tipo', 
        string=u'Tipo de Movimentação')
    tipo_prazo_id = fields.Many2one(
        comodel_name='tipo.prazo', 
        string=u'Tipo de Prazo')
    tipo_transito_id = fields.Many2one(
        comodel_name='tipo.transito', 
        string=u'Tipo de Trânsito')
    tipo_recurso_id = fields.Many2one(
        comodel_name='tipo.recurso', 
        string=u'Tipo de Recurso')
    tem_audiencia = fields.Selection(
        selection=boolean_selection_vals,
        string=u'Tem Audiência?')
    tipo_audiencia_id = fields.Many2one(
        comodel_name='tipo.audiencia', 
        string=u'Tipo de Audiência')
    tem_pagamento = fields.Selection(
        selection=boolean_selection_vals,
        string=u'Tem Pagamento?')
    tipo_pagamento_id = fields.Many2one(
        comodel_name='tipo.pagamento', 
        string=u'Tipo de Pagamento')
    tem_levantamento = fields.Selection(
        selection=boolean_selection_vals,
        string=u'Tem Levantamento?')
    tipo_levantamento_id = fields.Many2one(
        comodel_name='tipo.levantamento', 
        string=u'Tipo de Levantamento')
    tem_encerramento = fields.Selection(
        selection=boolean_selection_vals,
        string=u'Tem Encerramento?')
    tipo_encerramento_id = fields.Many2one(
        comodel_name='tipo.encerramento', 
        string=u'Tipo de Encerramento')
    tipo_sentenca_id = fields.Many2one(
        comodel_name='tipo.sentenca', 
        string=u'Tipo de Sentença')
    tipo_acordao_id = fields.Many2one(
        comodel_name='tipo.acordao', 
        string=u'Tipo de Acordão')
    task_id = fields.Many2one(
        comodel_name='project.task', 
        string=u'Compromisso')
    action_line_id = fields.Many2one(
        comodel_name='project.task.action.line', 
        string=u'Ação')
    incongruencia_id = fields.Many2one(
        comodel_name='dossie.fase.historico.erro', 
        string=u'Incongruência')
    erro = fields.Char(
        related='incongruencia_id.erro', 
        store=True)
    resolvido = fields.Selection(
        related='incongruencia_id.resolvido', 
        store=True)
    lido = fields.Boolean(
        string=u'Lido')

    def test_action_line(self):
        record = self
        self.env['project.task.action.line'].create({
            'movimentacao_id': record.id,
            'dossie_id': record.dossie_id and record.dossie_id.id or False,
        })

    def _process_dossie_movimentacao(self, movimentacao):
        # lock.acquire()
        with api.Environment.manage():
            with odoo.registry(self.env.cr.dbname).cursor() as new_cr:
                new_env = api.Environment(
                    new_cr, self.env.uid, self.env.context)
                try:
                    _logger.info(u'processing ' + str(movimentacao.id))
                    tipo_name = movimentacao.tipo_movimentacao_id.name
                    found = False
                    task_id = False
                    for task in movimentacao.dossie_id.task_ids:
                        if task.task_type_id.name == tipo_name:
                            found = True
                            task_id = task.id
                            break

                    action_id = self.with_env(new_env)['project.task.action'].search(
                        [('name', '=', u'Ler Movimentação')], limit=1)

                    if found:
                        action_line = self.with_env(new_env)['project.task.action.line'].create({
                            'movimentacao_id': movimentacao.id,
                            'action_id': action_id and action_id.id or False,
                            'dossie_id': movimentacao.dossie_id and movimentacao.dossie_id.id or False,
                            'task_id': task_id,
                        })
                        if action_line:
                            movimentacao.with_env(new_env).write(
                                {'action_line_id': action_line.id})
                        if task_id:
                            movimentacao.with_env(new_env).write(
                                {'task_id': action_line.task_id.id})
                    else:
                        task_type_id = self.with_env(new_env)['task.type'].search(
                            [('name', '=', tipo_name)], limit=1)
                        task = self.with_env(new_env)['project.task'].create({
                            'movimentacao_id': movimentacao.id,
                            'name': movimentacao.dossie_id.name,
                            'task_type_id':  task_type_id and task_type_id.id or False,
                            'dossie_id': movimentacao.dossie_id and movimentacao.dossie_id.id or False,
                            'tipo_prazo_id':  tipo_prazo_id and tipo_prazo.id or False,
                            'tipo_recurso_id':  tipo_recurso_id and tipo_recurso.id or False,
                        })

                        movimentacao.with_env(new_env).write(
                            {'task_id': task.id})
                except Exception, e:
                    new_env.cr.rollback()
                else:
                    new_env.cr.commit()

        # lock.release()
        return

    def _cron_dossie_movimentacao(self):
        _logger.info(u'Starting cron job on Dossiê Movimentação...')
        start_time = time.time()
        movimentacaos = self.search([])
        _logger.info(u'There are: ' + str(len(movimentacaos.ids)
                                          ) + ' records to process.. ')
        workers = []
        #lock = multiprocessing.Lock()
        #pool = multiprocessing.Pool(processes = multiprocessing.cpu_count()-1)
        for movimentacao in movimentacaos:
            thread = threading.Thread(
                target=self._process_dossie_movimentacao, args=(movimentacao,))
            thread.start()
            workers.append(thread)
        for t in workers:
            t.join()

            # self._process_dossie_movimentacao(movimentacao)
            #_logger.info(u'Running job on Movimentação with ID: ' + str(movimentacao.id))
            #process = multiprocessing.Process(target=self._process_dossie_movimentacao, args=(lock, movimentacao))
            # process.start()
            # workers.append(process)
            # workers.append(process)
        # for process in workers:
        #	process.join()
            #pool.apply_async(self._process_dossie_movimentacao, movimentacao)
        # pool.close()
        # pool.join()
            # self._process_dossie_movimentacao(movimentacao)
        m, s = divmod((time.time() - start_time), 60)
        h, m = divmod(m, 60)
        processing_time = "%02d:%02d:%02d" % (h, m, s)
        _logger.info(
            u'Ending cron job on Dossiê Movimentação with processing time: ' + str(processing_time))
        return

########## PEDIDOS ##########


class DossiePedidoTipo(models.Model):
    _name = 'dossie.pedido.tipo'
    _description = u'Tipo de Pedido'

    name = fields.Char(
        string=u'Nome')


class DossiePedido(models.Model):
    _name = 'dossie.pedido'
    _description = u'Pedido'

    name = fields.Char(
        string=u'Nome', 
        compute='get_pedido_name', 
        store=True)
    tipo_id = fields.Many2one(
        comodel_name='dossie.pedido.tipo', 
        string=u'Tipo')
    valor = fields.Monetary(
        string=u'Valor', currency_field='currency_id')
    valor_media = fields.Monetary(
        string=u'Média Valor',
        related='valor', 
        group_operator='avg',
        readonly=True, 
        store=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    dossie_id = fields.Many2one(
        comodel_name='dossie.dossie', 
        string=u'Dossiê', 
        ondelete='cascade')

    @api.one
    @api.depends('tipo_id', 'dossie_id', 'valor', 'currency_id')
    def get_pedido_name(self):
        name = self.tipo_id.name or ' '
        currency = self.currency_id.symbol or ' '
        if self.dossie_id:
            name = name + ' | ' + str(self.currency_id) + ' ' + str(self.valor)
        self.name = name


########## CITAÇÃO ##########


class DossieCitacaoTipo(models.Model):
    _name = 'dossie.citacao.tipo'
    _description = u'Tipo de Citacao'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class DossieCitacaoParte(models.Model):
    _name = 'dossie.citacao.parte'
    _description = u'Partes Citadas'

    parte_contraria_id = fields.Many2one(
        comodel_name='res.partner', 
        string=u'Parte Contrária')
    state = fields.Selection(
        string=u'Situação', 
        selection=[('c', u'Citado'), ('nc', u'Não Citado')])
    citacao_id = fields.Many2one(
        comodel_name='dossie.citacao', 
        string=u'Citaçao')
    related_parte_contraria_ids = fields.Many2many(
        related='citacao_id.parte_contraria_ids')
    task_id = fields.Many2one(
        comodel_name='project.task', 
        string=u'Compromisso',
        ondelete='cascade')


class DossieCitacao(models.Model):
    _name = 'dossie.citacao'
    _description = u'Citação'

    name = fields.Char(
        string=u'Nome', 
        compute='get_citacao_name', 
        store=True)
    data = fields.Date(
        string=u'Data do Pedido')
    resultado_parte_ids = fields.One2many(
        comodel_name='dossie.citacao.parte', 
        inverse_name='citacao_id', 
        string=u'Partes Citadas')
    parte_contraria_ids = fields.Many2many(
        comodel_name='res.partner', 
        string=u'Partes a Citar')
    tipo_id = fields.Many2one(
        comodel_name='dossie.citacao.tipo', 
        string=u'Tipo',
        required=True)
    dossie_id = fields.Many2one(
        comodel_name='dossie.dossie', 
        string=u'Dossiê', 
        ondelete='cascade')
    task_id = fields.Many2one(
        comodel_name='project.task', 
        string=u'Compromisso', 
        ondelete='cascade')
    state = fields.Selection(
        string=u'Estado', 
        selection=[('ad', u'Aguardando Deferimento'), ('ae', u'Aguardando Expedição'), ('ae', u'Aguardando Efetivação'), ('pc', u'Parcialmente Citado'), ('c', u'Citado'), ('nc', u'Não Citado')],
        default='ad')
    related_parte_contraria_ids = fields.Many2many(
        comodel_name='res.partner', 
        related='dossie_id.parte_contraria_ids',
        string='Related Parte Contraria')

    @api.one
    @api.depends('tipo_id', 'dossie_id')
    def get_citacao_name(self):
        name = self.tipo_id.name or ' '
        if self.dossie_id:
            name = name + ' | ' + self.dossie_id.name
        self.name = name


########## PENHORA ##########


class DossiePenhoraTipo(models.Model):
    _name = 'dossie.penhora.tipo'
    _description = u'Tipo de Penhora'

    name = fields.Char(
        string=u'Nome', 
        required=True)


class DossiePenhora(models.Model):
    _name = 'dossie.penhora'
    _description = u'Penhora'

    name = fields.Char(
        string=u'Nome', 
        compute='get_citacao_name', 
        store=True)
    parte_contraria_ids = fields.Many2many(
        comodel_name='res.partner', 
        relation='parte_contraria_penhora_rel',
        column1='parte_contraria_id', 
        column2='penhora_id', 
        string=u'Partes')
    bem_ids = fields.Many2many(
        comodel_name='res.partner.asset', 
        relation='bens_penhora_rel', 
        column1='bem_id', 
        column2='penhora_id', 
        string=u'Bens')
    dossie_id = fields.Many2one(
        comodel_name='dossie.dossie', 
        string=u'Dossiê', 
        ondelete='cascade')
    task_id = fields.Many2one(
        comodel_name='project.task', 
        string=u'Compromisso', 
        ondelete='cascade')
    state = fields.Selection(
        selection=dossie_penhora_state_vals,
        string=u'Estado', 
        default='ad')
    valor = fields.Monetary(
        string=u'Valor Levantado', 
        currency_field='currency_id', 
        compute='_get_value', 
        store=True)
    valor_media = fields.Monetary(
        string=u'Média Valor',
        related='valor', 
        group_operator='avg',
        readonly=True, 
        store=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    data = fields.Date(
        string=u'Data da Penhora')
    tipo_ids = fields.Many2many(
        comodel_name='dossie.penhora.tipo', 
        relation='penhora_tipo_rel', 
        column1='tipo_id', 
        column2='penhora_id',
        string=u'Tipos de Penhora')
    related_parte_contraria_ids = fields.Many2many( 
        related='dossie_id.parte_contraria_ids')

    @api.one
    @api.depends('dossie_id', 'tipo_ids')
    def get_citacao_name(self):
        name = ', '.join(type.name for type in self.tipo_ids)
        if self.dossie_id:
            name = name + ' | ' + self.dossie_id.name
        self.name = name

    @api.one
    @api.depends('bem_ids')
    def _get_value(self):
        total = 0
        for bem in self.bem_ids:
            total += bem.value
        self.valor = total

########## HISTÓRICO DE FASE ##########


class DossieFaseHistorico(models.Model):
    _name = 'dossie.fase.historico'

    dossie_id = fields.Many2one(
        comodel_name='dossie.dossie', 
        string=u'Dossie')
    data = fields.Date(
        string=u'Data')
    movimentacao_id = fields.Many2one(
        comodel_name='dossie.movimentacao', 
        string=u'Movimentação')
    fase_id = fields.Many2one(
        comodel_name='dossie.fase', 
        string=u'Fase Atual')
    fase_id_bkp = fields.Many2one(
        related='dossie_id.fase_id_bkp')
    movimentacao = fields.Text(
        related='movimentacao_id.movimentacao')
    tem_pagamento = fields.Selection(
        store=True,
        related='dossie_id.tem_pagamento')
    tem_garantia = fields.Selection(
        related='dossie_id.tem_garantia', 
        store=True)


class DossieFaseHistoricoErro(models.Model):
    _name = 'dossie.fase.historico.erro'

    dossie_id = fields.Many2one(
        comodel_name='dossie.dossie', 
        string=u'Dossie')
    data = fields.Date(
        string=u'Data')
    movimentacao_id = fields.Many2one(
        comodel_name='dossie.movimentacao', 
        string=u'Movimentação')
    fase_id = fields.Many2one(
        comodel_name='dossie.fase', 
        string=u'Fase Atual')
    fase_id_bkp = fields.Many2one(
        related='dossie_id.fase_id_bkp')
    movimentacao = fields.Text(
        related='movimentacao_id.movimentacao')
    erro = fields.Char(
        string=u'Incongruência')
    resolvido = fields.Selection(
        selection=boolean_selection_vals,
        string=u'Resolvido',
        required=True)
    tem_pagamento = fields.Selection( 
        store=True,
        related='dossie_id.tem_pagamento')
    tem_garantia = fields.Selection(
        related='dossie_id.tem_garantia', 
        store=True)


class DossieFaseClienteConfig(models.Model):
    _name = 'dossie.fase.cliente.config'
    _description = 'Dossie Fase Cliente Config'

    dominio = fields.Text(u'Dominio', default="[]")
    name = fields.Char(u'Nome da Fase')
