/*
 * This file is part of Zenodo.
 * Copyright (C) 2014 CERN.
 *
 * Zenodo is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Zenodo is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
 *
 * In applying this licence, CERN does not waive the privileges and immunities
 * granted to it by virtue of its status as an Intergovernmental Organization
 * or submit itself to any jurisdiction.
 */

define(function(require) {
    'use strict';

    /**
     * Module dependencies
     */
    var defineComponent = require('flight/lib/component');

    /**
     * Module exports
     */
    return defineComponent(citationformatter);

    /**
     * Module function
     */
    function citationformatter() {
        this.attributes({
            stylesSelector: '.styles',
            citationSelector: '.citation',
            lang: 'en-US',
            apiUrl: '/citeproc/format'
        });

        /**
         * Internal methods
         */
        this.formatDoi = function(doi_val, style_val) {
            var component = this;

            $.ajax({
                type: 'GET',
                url: this.attr.apiUrl,
                dataType: "text",
                data: {
                    doi: doi_val,
                    style: style_val,
                    lang: this.attr.lang
                },
                success: function(data){
                    component.trigger("citationChanged", {citation: data});
                }
            });
        };

        /**
         * Event handler
         */
        this.onSelectStyle = function() {
            this.formatDoi(
                this.$node.data('doi'),
                this.select('stylesSelector').val()
            );
        }

        this.onCitationChanged = function(e, payload) {
            this.select('citationSelector').text(payload.citation);
        }

        /**
         * Initialize component
         */
        this.after('initialize', function() {
            this.on(
                this.attr.stylesSelector,
                'change',
                this.onSelectStyle
            );

            this.on(
                'citationChanged',
                this.onCitationChanged
            );
        });
    }
});
