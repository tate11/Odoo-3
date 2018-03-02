odoo.define('studio_backend_theme_v10.UserMenu', function (require) {
"use strict";

var core = require('web.core');
var Dialog = require('web.Dialog');
var UserMenu = require('web.UserMenu');

var _t = core._t;
var QWeb = core.qweb;

UserMenu.include({
    on_menu_support: function () {
        window.location.href = 'mailto:help@odoo.com';
    },
    on_menu_shortcuts: function() {
        new Dialog(this, {
            size: 'large',
            dialogClass: 'o_act_window',
            title: _t("Keyboard Shortcuts"),
            $content: $(QWeb.render("UserMenu.shortcuts"))
        }).open();
    },
});

});

//***************************************

odoo.define('studio_backend_theme_v10.DebugManager', function (require) {
"use strict";

var core = require('web.core');
var WebClient = require('web.WebClient');

if (core.debug) {
    WebClient.include({
        start: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                var toggle_app_changer = self.toggle_app_changer;
                self.toggle_app_changer = function(display) {
                    var action;
                    if (!display) {
                        action = self.action_manager.get_inner_action();
                    }
                    self.current_action_updated(action);
                    toggle_app_changer.apply(self, arguments);
                };
            });
        },
        instanciate_menu_widgets: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function() {
                self.systray_menu = self.menu.systray_menu;
            });
        },
    });
}

});
