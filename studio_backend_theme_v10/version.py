# -*- coding: utf-8 -*-

import odoo

# ----------------------------------------------------------
# Monkey patch release to set the edition as 'Professional'
# ----------------------------------------------------------
odoo.release.version_info = odoo.release.version_info[:5] + ('pro',)
if '+e' not in odoo.release.version:     # not already patched by packaging
    odoo.release.version = '{0}+pro{1}{2}'.format(*odoo.release.version.partition('-'))

odoo.service.common.RPC_VERSION_1.update(
    server_version=odoo.release.version,
    server_version_info=odoo.release.version_info)
