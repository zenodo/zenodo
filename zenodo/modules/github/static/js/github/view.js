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
    require('bootstrap-switch');

    return function(config) {
        init_switches(config);
        init_syncbutton(config);


        $("i.error").tooltip({
            trigger: "hover",
            animation: true,
            placement: "top",
        });

        $('[data-toggle="tooltip"]').tooltip();
    };

    function init_syncbutton(config){
        var syncButton = $(config.sync_button);

        syncButton.on("click", function() {
            $.ajax({
                url: config.sync_url,
                type: "POST",
                success: function(data, textStatus, jqXHR) {
                    $(config.github_view).html(data);
                    init_switches();
                }
            });
        });
    }

    function init_switches(config){
        // Initialize bootstrap switches
        var test_switch = $("input[name='test-flip']").bootstrapSwitch();
        var doiSwitches = $("input[data-repo-name]").bootstrapSwitch();
        doiSwitches.on("switchChange.bootstrapSwitch", function(e, state) {
            var repoName = e.target.dataset.repoName;
            var method = state ? "POST" : "DELETE";

            console.log(method, " to ", config.hook_url);

            $.ajax({
                url: config.hook_url,
                type: method,
                data: JSON.stringify({repo: repoName}),
                contentType: "application/json; charset=utf-8",
                dataType: "json",

                success: function(data, textStatus, jqXHR) {
                    var status = "fa-exclamation";
                    if(jqXHR.status == 204 || jqXHR.status==201){
                        status =  "fa-check";
                    }

                    // Select the correct toggle
                    var el = $("[data-repo='" + repoName + "'] .hook-status");
                    el.addClass(status);
                    el.animate({
                        opacity: 0
                    }, 2000, function() {
                        el.removeClass(status);
                        el.css('opacity', 1);
                    });
                }
            });

        });
    }
})