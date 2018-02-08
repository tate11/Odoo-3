odoo.define('lincer_board.dashboard', function (require) {
"use strict";

var ActionManager = require('web.ActionManager');
var core = require('web.core');
var data = require('web.data');
var Dialog = require('web.Dialog');
var FavoriteMenu = require('web.FavoriteMenu');
var form_common = require('web.form_common');
var Model = require('web.DataModel');
var pyeval = require('web.pyeval');
var ViewManager = require('web.ViewManager');
var data_manager = require('web.data_manager');

var _t = core._t;
var QWeb = core.qweb;

FavoriteMenu.include({
    init: function (parent, query, target_model, action_id, filters) {
        var self = this;
        this._super.apply(this,arguments);
        this.board_views = [];
    },

    start: function () {
        var self = this;
        this._super();
        var def = new $.Deferred();
        new Model('ir.ui.view').call('search_read', [[['model', '=', 'board.board']],["name", "id"]]).then(function(items){
            // self.board_views = result;
            var elm = self.$add_to_dashboard && self.$add_to_dashboard.find('.o_add_board_board_views');
            if (elm){
                _.each(items, function (item) {
                elm.append($('<option>', { 
                    id: item.id,
                    text : item.name 
                    }));
                });
            };
            def.resolve();
        });
    },
    add_dashboard: function () {
        var self = this;
        var search_data = this.searchview.build_search_data(),
            context = new data.CompoundContext(this.searchview.dataset.get_context() || []),
            domain = new data.CompoundDomain(this.searchview.dataset.get_domain() || []);
        _.each(search_data.contexts, context.add, context);
        _.each(search_data.domains, domain.add, domain);

        context.add({
            group_by: pyeval.eval('groupbys', search_data.groupbys || [])
        });
        context.add(this.view_manager.active_view.controller.get_context());
        var c = pyeval.eval('context', context);
        for(var k in c) {
            if (c.hasOwnProperty(k) && /^search_default_/.test(k)) {
                delete c[k];
            }
        }
        this.toggle_dashboard_menu(false);

        c.dashboard_merge_domains_contexts = false;
        var d = pyeval.eval('domain', domain),
            board = new Model('board.board'),
            name = self.$add_dashboard_input.val();

        
        var ctx_view_id= this.$('.o_board_view_selector').find(':selected')[0]['id'];
        if (ctx_view_id){
            ctx_view_id = parseInt(ctx_view_id);
            c['ctx_view_id'] = ctx_view_id;
        };
        

        return self.rpc('/board/add_to_dashboard', {
            action_id: self.action_id || false,
            context_to_save: c,
            domain: d,
            view_mode: self.view_manager.active_view.type,
            name: name,
        }).then(function (r) {
            if (r) {
                self.do_notify(_.str.sprintf(_t("'%s' added to dashboard"), name), '');
                data_manager.invalidate();
            } else {
                self.do_warn(_t("Could not add filter to dashboard"));
            }
            });
        },
    });

});
