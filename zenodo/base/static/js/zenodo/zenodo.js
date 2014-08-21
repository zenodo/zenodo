/*
 * This file is part of ZENODO.
 * Copyright (C) 2014 CERN.
 *
 * ZENODO is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * ZENODO is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
 *
 * In applying this licence, CERN does not waive the privileges and immunities
 * granted to it by virtue of its status as an Intergovernmental Organization
 * or submit itself to any jurisdiction.
 */

 define(function(require, exports, module) {
    'use strict';

    var $ = require('jquery');

    var alert_template = require('hgn!./templates/alert');
    var tag_templates = {
        'funding_source': require('hgn!./templates/funding_source'),
        'collections': require('hgn!./templates/collections')
    };
    var ajaxmsg_template = require('hgn!./templates/ajaxmsg');


    $(document).ready(function(){
        $('#affix-outer').height($('#navbar').height());

        $('#author_affiliations_link').click(function() {
            $('#authors_short').toggle('slow', function() {
                if ($('#author_affiliations_link').html() == "(hide affiliations)") {
                    $('#author_affiliations_link').html("(show affiliations)");
                } else {
                    $('#author_affiliations_link').html("(hide affiliations)");
                }
            });
            $('#authors_long').toggle('slow', function() {});
        });
    });

    $(document).ready(function(){
        $(".accept-coll-btn").click(function(e){
            community_approval(this,"accept");
            e.preventDefault();
        });
        $(".reject-coll-btn").click(function(e){
            community_approval(this,"reject");
            e.preventDefault();
        });
        $(".remove-coll-btn").click(function(e){
            community_approval(this,"remove");
            e.preventDefault();
        });
    });

    $(document).ready(function(){
        /*
        * https://github.com/twbs/bootstrap/issues/6350
        * Clamped-width.
        * Usage:
        *  <div data-clampedwidth=".myParent">This long content will force clamped width</div>
        *
        * Author: LV
        */
        $('[data-clampedwidth]').each(function () {
            var elem = $(this);
            var parentPanel = elem.data('clampedwidth');
            var resizeFn = function () {
                var sideBarNavWidth = $(parentPanel).width() - parseInt(elem.css('paddingLeft')) - parseInt(elem.css('paddingRight')) - parseInt(elem.css('marginLeft')) - parseInt(elem.css('marginRight')) - parseInt(elem.css('borderLeftWidth')) - parseInt(elem.css('borderRightWidth'));
                elem.css('width', sideBarNavWidth);
            };

            resizeFn();
            $(window).resize(resizeFn);
        });
    });


    var datepicker_config = {
        element: '.datepicker',
        options: {
            format: 'yyyy-mm-dd',
            weekStart: 1,
            autoclose: true,
            todayBtn: "linked",
            todayHighlight: true,
            keyboardNavigation: true
        }
    };
    module.exports.datepicker_config = datepicker_config;

    function community_approval(btn, action) {
        recid = $(btn).data('recid');
        coll = $(btn).data('collection');
        url = $(btn).data('url');
        spanid = "#curate_"+recid+"_"+coll;
        if(action == 'remove'){
            spanid = spanid + "_rm";
        }

        $(spanid + " .loader").addClass("loading");
        $.ajax({
            url: url,
            type: 'POST',
            cache: false,
            data: $.param({'action': action, 'recid': recid, 'collection': coll}),
            dataType: 'json'
        }).done(function(data) {
            if(data.status == 'success' ){
                set_community_buttons(spanid, action);
            } else {
                set_ajaxmsg(spanid, "Server problem ", "warning-sign");
            }
            $(spanid + " .loader").removeClass("loading");
        }).fail(function(data) {
            set_ajaxmsg(spanid, "Server problem ", "warning-sign");
            $(spanid + " .loader").removeClass("loading");
        });
    }

    function set_ajaxmsg(selector, message, icon){
        $(selector+ " .ajaxmsg").show();
        $(selector+ " .ajaxmsg").html(ajaxmsg_template.render({"message": message, "icon": icon}));
    }

    function set_community_buttons(selector, action) {
        // Disabled buttons
        $(selector+ " .btn").attr('disabled', '');
        // Show selected
        if(action=="accept"){
            $(selector+ " ."+action+"-coll-btn").addClass('btn-success','');
        } else {
            $(selector+ " ."+action+"-coll-btn").addClass('btn-danger','');
        }
    }
})