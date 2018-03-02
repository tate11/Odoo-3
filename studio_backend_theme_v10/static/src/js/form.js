odoo.define('studio_backend_theme_v10.FormView', function (require) {
"use strict";

var config = require('web.config');
var FormRenderingEngineMobile = require('studio_backend_theme_v10.FormRenderingEngineMobile');
var FormView = require('web.FormView');

FormView.include({
    defaults: _.extend({}, FormView.prototype.defaults, {
        disable_autofocus: config.device.touch,
    }),
    init: function () {
        this._super.apply(this, arguments);
        if (config.device.size_class <= config.device.SIZES.XS) {
            this.rendering_engine = new FormRenderingEngineMobile(this);
        }
    },
});

});


odoo.define('studio_backend_theme_v10.FormRenderingEngine', function (require) {
"use strict";

var config = require('web.config');
var core = require('web.core');
var FormRenderingEngine = require('web.FormRenderingEngine');

var _t = core._t;

FormRenderingEngine.include({
    process: function($tag) {
        var self = this;
        // Add button box post rendering when window resize and record loaded events
        if($tag.attr("name") === 'button_box') {
            this.view.is_initialized.then(function() {
                var $buttons = $tag.children();
                self.organize_button_box($tag, $buttons);

                self.view.on('view_content_has_changed', self, function() {
                    this.organize_button_box($tag, $buttons);
                });
                core.bus.on('size_class', self, function() {
                    this.organize_button_box($tag, $buttons);
                });
            });
        }
        return this._super($tag);
    },
    organize_button_box: function($button_box, $buttons) {
        var $visible_buttons = $buttons.not('.o_form_invisible');
        var $invisible_buttons = $buttons.filter('.o_form_invisible');

        // Get the unfolded buttons according to window size
        var nb_buttons = [2, 4, 6, 7][config.device.size_class];
        var $unfolded_buttons = $visible_buttons.slice(0, nb_buttons).add($invisible_buttons);

        // Get the folded buttons
        var $folded_buttons = $visible_buttons.slice(nb_buttons);
        if($folded_buttons.length === 1) {
            $unfolded_buttons = $buttons;
            $folded_buttons = $();
        }

        // Empty button box and toggle class to tell if the button box is full (LESS requirement)
        $buttons.detach();
        $button_box.empty();
        var full = ($visible_buttons.length > nb_buttons);
        $button_box.toggleClass('o_full', full).toggleClass('o_not_full', !full);

        // Add the unfolded buttons
        $unfolded_buttons.each(function(index, elem) {
            $(elem).appendTo($button_box);
        });

        // Add the dropdown with unfolded buttons if any
        if($folded_buttons.length) {
            $button_box.append($("<button/>", {
                type: 'button',
                'class': "btn btn-sm oe_stat_button o_button_more dropdown-toggle",
                'data-toggle': "dropdown",
                text: _t("More"),
            }));

            var $ul = $("<ul/>", {'class': "dropdown-menu o_dropdown_more", role: "menu"}).appendTo($button_box);
            $folded_buttons.each(function(i, elem) {
                $('<li/>').appendTo($ul).append(elem);
            });
        }
    },
    process_header: function($statusbar) {
        var $new_statusbar = this.render_element('FormRenderingStatusBar', $statusbar.getAttributes());
        this.handle_common_properties($new_statusbar, $statusbar);
        $statusbar.find('button').addClass('o_in_statusbar');
        this.fill_statusbar_buttons($new_statusbar.find('.o_statusbar_buttons'), $statusbar.contents('button'));
        $new_statusbar.append($statusbar.find('field'));
        $statusbar.before($new_statusbar).remove();
        this.process($new_statusbar);
    },
    fill_statusbar_buttons: function($statusbar_buttons, $buttons) {
        $statusbar_buttons.append($buttons);
    },
    process_button: function ($button) {
        $button = this._super($button);
        if ($button.hasClass('oe_highlight')) {
            $button.addClass('btn-primary');
        } else if ($button.hasClass('o_in_statusbar')) {
            $button.addClass('btn-default');
        }
        $button.removeClass('o_in_statusbar oe_highlight');
        return $button;
    }
});

});

odoo.define('studio_backend_theme_v10.FormRenderingEngineMobile', function (require) {
"use strict";

var FormRenderingEngine = require('web.FormRenderingEngine');

return FormRenderingEngine.extend({
    fill_statusbar_buttons: function ($statusbar_buttons, $buttons) {
        if(!$buttons.length) {
            return;
        }
        var $statusbar_buttons_dropdown = this.render_element('FormRenderingStatusBar_DropDown', {});
        $buttons.each(function(i, el) {
            $statusbar_buttons_dropdown.find('.dropdown-menu').append($('<li/>').append(el));
        });
        $statusbar_buttons.append($statusbar_buttons_dropdown);
    },
});

});

//*******************************************************
odoo.define('studio_backend_theme_v10.form_widgets', function (require) {
"use strict";

var config = require('web.config');
var core = require('web.core');
var form_widgets = require('web.form_widgets');

var QWeb = core.qweb;

form_widgets.FieldStatus.include({
    template: undefined,
    className: "o_statusbar_status",
    render_value: function() {
        var self = this;
        var $content = $(QWeb.render("FieldStatus.content." + ((config.device.size_class <= config.device.SIZES.XS)? 'mobile' : 'desktop'), {
            'widget': this, 
            'value_folded': _.find(this.selection.folded, function (i) {
                return i[0] === self.get('value');
            }),
        }));
        this.$el.empty().append($content.get().reverse());
    },
    bind_stage_click: function () {
        this.$el.on('click','button[data-id]',this.on_click_stage);
    },
});

var FieldPhone = form_widgets.FieldEmail.extend({
    prefix: 'tel',
    init: function() {
        this._super.apply(this, arguments);
        this.clickable = config.device.size_class <= config.device.SIZES.XS;
    },
    render_value: function() {
        this._super();
        if(this.clickable) {
            var text = this.$el.text();
            this.$el.html(text.substr(0, text.length/2) + "&shy;" + text.substr(text.length/2)); // To prevent Skype app to find the phone number
        }
    }
});

core.form_widget_registry
    .add('phone', FieldPhone)
    .add('upgrade_boolean', form_widgets.FieldBoolean) // community compatibility
    .add('upgrade_radio', form_widgets.FieldRadio); // community compatibility

});