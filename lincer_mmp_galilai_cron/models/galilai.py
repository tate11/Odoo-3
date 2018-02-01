
# -*-coding:utf-8-*-
from odoo import models, fields, api, _
import odoo
import logging
from datetime import datetime
import threading
from Queue import Queue
import multiprocessing
import time
from contextlib import closing


_logger = logging.getLogger(__name__)
_CONVERTED = u'Converted'

class GalilaiTestModel(models.Model):
    _inherit = 'galilai.test.model'

    def _run_lincer_mmp_galilai(self, queue):
        global count
        global size
        if queue:
            #with semaphores:
            #    with multiprocessing.Lock():
            with api.Environment.manage():
                with odoo.registry(self.env.cr.dbname).cursor() as new_cr:
                    self = self.with_env(self.env(cr=new_cr))
                    g = self.env['galilai.test.model'].browse(queue)
                    _logger.info(u'Processing [%s] - %s/%s (%s%s)...' %(g.id, count, size, 100 * count/size,'%'))
                    count += 1
                    grupo = estado = orgao = vara = False
                    try:
                        grupo = self.env['res.partner'].search([('name','=',g.field2)], limit=1)
                        if not grupo:
                            grupo = self.env['res.partner'].create({'name':g.field2})
                    except Exception, err:
                        raise Warning(u"ERRO res.partner :\n%s" % err[0])

                    try:
                        estado = self.env['res.country.state'].search([('name','ilike',g.field3)], limit=1)
                        if not estado:
                            estado = self.env['res.country.state'].create({'name':g.field3})
                    except Exception, err:
                        raise Warning(u"ERRO res.country.state :\n%s" % err[0])

                    try:
                        orgao = self.env['dossie.orgao'].search([('name','=',g.field5)], limit=1)
                        if not orgao:
                            orgao = self.env['dossie.orgao'].create({'name':g.field5})
                    except Exception, err:
                        raise Warning(u"ERRO dossie.orgao :\n%s" % err[0])

                    try:
                        vara = self.env['dossie.vara'].search([('name','=',g.field6)], limit=1)
                        if not vara:
                            vara = self.env['dossie.vara'].create({'name':g.field6})
                    except Exception, err:
                        raise Warning(u"ERRO dossie.vara :\n%s" % err[0])

                    if grupo and estado and orgao and vara:
                        try:
                            dossie = self.env['dossie.dossie'].search([('name','=',g.field7)], limit=1)
                            if not dossie:
                                dossie = self.env['dossie.dossie'].create({'grupo_id':grupo.id,'estado_id':estado.id,'orgao_id':orgao.id,'vara_id':vara.id, 'processo':g.field7, 'name':g.field7})
                        except Exception, err:
                            raise Warning(u"ERRO dossie.dossie :\n%s" % err[0])

                        try:   
                            movimentacao = self.env['dossie.movimentacao'].create({'dossie_id':dossie.id, 'data':datetime.strptime(g.field4, '%d/%m/%Y').date(), 'movimentacao':g.field8})
                        except Exception, err:
                            raise Warning(u"ERRO dossie.movimentacao :\n%s" % err[0])

                    #g.write({'field9':_CONVERTED})
                    new_cr.commit()
            #queue.task_done()
        return True

    def _cron_lincer_mmp_galilai(self, limit=0, cores=8):
        global count
        global size
        t1 = time.time()
        _logger.info(u'Starting cron job on Galilai Test Model...')
        nprocesses = multiprocessing.cpu_count()
        semaphore_pool = multiprocessing.BoundedSemaphore(nprocesses)
        queue = []
        galilai = []
        if limit:
            galilai = self.search([('field9','=',False)], limit=limit)
        else:
            galilai = self.search([('field9','=',False)])
        
        size = len(galilai)
        count = 1
        _logger.info(u'Processing [%s] Galilai test model records...' %size)

        for g in galilai:
            queue.append(g.id)

        processes = []

        with closing(multiprocessing.Pool(processes=2)) as pool:
            pool.map(self._run_lincer_mmp_galilai, queue)
            pool.apply_async(foo.work)
            pool.close()
            pool.join()

        """for i in range(nprocesses):
            process = multiprocessing.Process(target=self._run_lincer_mmp_galilai, name=u'_run_lincer_mmp_galilai_' + str(i+1), 
                args=(semaphore_pool, queue))
            process.daemon  = True
            process.start()"""
        
        #for process in processes:
        #    process.daemon = True
        #    process.start()

        #for process in processes:
        #    process.join()

        #queue.join()
        _logger.info(u'It took %s secs to process %s records.' %(time.time() - t1, size))
        _logger.info(u'Ending cron job on Galilai Test Model...')

        return True