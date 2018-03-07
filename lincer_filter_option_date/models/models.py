# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta
import re

from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, \
    DEFAULT_SERVER_DATE_FORMAT

RELATIVEDELTA_TYPES = {
    'Y': 'years',
    'm': 'months',
    'W': 'weeks',
    'd': 'days',
    'H': 'hours',
    'M': 'minutes',
}

native_where_calc = models.BaseModel._where_calc


@api.model
def _where_calc(self, domain, active_test=True):
    match_pattern = re.compile('^[+-]{0,1}[0-9]*[YmWdHM]$')
    group_pattern = re.compile(
        r'(?P<value>^[+-]{0,1}[0-9]*)(?P<type>[%s]$)' % ''.join(
            RELATIVEDELTA_TYPES.keys()))
    for cond in domain or []:
        if isinstance(cond, (tuple, list)) and \
            isinstance(cond[2], basestring) and \
                match_pattern.match(cond[2]):
            value_format = None
            model = self._name
            for fieldname in cond[0].split('.'):
                field = self.env[model]._fields[fieldname]
                model = field.comodel_name
                if not model and field.type in ('datetime', 'date'):
                    value_format = field.type == 'date' and \
                        DEFAULT_SERVER_DATE_FORMAT or \
                        DEFAULT_SERVER_DATETIME_FORMAT
            if value_format:
                vals = group_pattern.match(cond[2]).groupdict()
                args = {RELATIVEDELTA_TYPES[vals['type']]: int(vals['value'])}
                cond[2] = (datetime.now() - relativedelta(**args)
                           ).strftime(value_format)
    return native_where_calc(self, domain, active_test)


models.BaseModel._where_calc = _where_calc
