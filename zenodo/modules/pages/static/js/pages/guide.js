/*
 * This file is part of Zenodo.
 * Copyright (C) 2015 CERN.
 *
 * Zenodo is free software; you can redistribute it and/or modify
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

require(['jquery'], function($) {
    /*
     * Sticky menu.
     */
    require(['jquery-pin'], function () {
        $(".sticky").pin({
            containerSelector: ".sticky-container",
            minWidth: 940
        });
    });

    /*
     * Back to top button.
     */
    $(document).ready(function() {
        var offset = 250;
        var duration = 300;
        $(window).scroll(function() {
            $('.back-to-top').css('bottom', $(window).height()/2);
            if ($(this).scrollTop() > offset && $(window).width() > 900) {
                $('.back-to-top').fadeIn(duration);
            } else {
                $('.back-to-top').fadeOut(duration);
            }
        });
        $(window).on('resize', function(){
            if ($(window).width() <= 900) {
                $('.back-to-top').hide();
            }
        });
        $('.back-to-top').click(function(event) {
            event.preventDefault();
            $('html, body').animate({scrollTop: 0}, duration);
            return false;
        })
    });


    /*
     * Build menu.
     */
    $(document).ready(function() {
        var lvl_1 = 'h2';
        var lvl_2 = 'h3';
        var lvl_3 = 'h4';
        var lvl_4 = 'h5';
        var stickyContainerSelector = '.sticky-container';

        var selector = [
            stickyContainerSelector + " " + lvl_1,
            stickyContainerSelector + " " + lvl_2,
            stickyContainerSelector + " " + lvl_3,
            stickyContainerSelector + " " + lvl_4
        ].join(', ');
        var elements = document.querySelectorAll(selector);
        var menuFragment = document.createDocumentFragment();

        $.each(elements, function (i, element) {
            var li = document.createElement('li');
            if (element.tagName === lvl_1.toUpperCase()) {
                cl = 'lvl-1';
            } else if (element.tagName === lvl_2.toUpperCase()) {
                cl = 'lvl-2';
            } else if (element.tagName === lvl_3.toUpperCase()) {
                cl = 'lvl-3';
            } else if (element.tagName === lvl_4.toUpperCase()) {
                cl = 'lvl-4';
            }
            if (cl) li.classList.add(cl);
            var a = document.createElement('a');
            a.innerText = element.innerText;
            var handler = (function (e) {
                return function () {
                    var body = $("html, body");
                    body.animate(
                        {scrollTop: $(e).offset().top}, '500', 'swing', function() {}
                    );
                }
            }(element));
            a.onclick = handler;
            li.appendChild(a);
            menuFragment.appendChild(li);
        });

        $('.sticky-list').append(menuFragment);
    });

});
