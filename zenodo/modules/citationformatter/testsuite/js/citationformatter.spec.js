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

'use strict';

describeComponent('js/citationformatter/citationformatter', function() {

    // Initialize the component and attach it to the DOM
    beforeEach(function() {
        jasmine.Ajax.install();
        this.setupComponent(
            '<div id="citationformatter" data-doi="10.1234/foo.bar">' +
            '<span class="citation"></span>' +
            '<select class="styles">' +
            '<option value="apa">apa</option>' +
            '<option value="nature">nature</option>' +
            '</select></div>');
    });

    afterEach(function() {
        jasmine.Ajax.uninstall();
    });

    it('should be defined', function() {
        expect(this.component).toBeDefined();
        expect(this.component.$node).toHaveId('citationformatter');
        expect(this.component.$node.data('doi')).toEqual('10.1234/foo.bar');
        expect(this.component.$node.find('.citation')).toBeDefined();
        expect(this.component.$node.find('.styles')).toBeDefined();
    });

    it('should set attr.stylesSelector', function() {
        this.setupComponent({
            stylesSelector: '.citation-styles-selector'
        });
        expect(this.component.attr.stylesSelector).toEqual(
            '.citation-styles-selector');
    });

    it('should update .citation on citationChanged', function() {
        this.component.trigger('citationChanged', {
            citation: 'this is a citation'
        });

        expect(this.component.select('citationSelector').html()).toEqual(
            'this is a citation');
    });

    it('should make ajax request using data-doi and style', function() {
        var $styles = this.component.select('stylesSelector'),
            $citation = this.component.select('citationSelector');

        $styles.trigger('change');

        var request = jasmine.Ajax.requests.mostRecent();
        expect(request.url).toBe('/citeproc/format?doi=10.1234%2Ffoo.bar&style=apa&lang=en-US');
        expect(request.method).toBe('GET');

        // Fake response
        request.response({
            status: 200,
            responseText: 'mycitation'
        })
        expect($citation.html()).toEqual("mycitation");
    });
});
