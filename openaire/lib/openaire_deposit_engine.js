/*
 * This file is part of Invenio.
 * Copyright (C) 2010, 2011 CERN.
 *
 * CDS Invenio is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * CDS Invenio is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 */

/* Global Tooltips configuration :-) */
var gTipDefault = {
    position: {
        corner: {
            target: 'bottomRight',
            tooltip: 'topLeft'
        }
    },
    adjust: {
        screen: true
    },
    hide: {
        fixed: true,
        delay: 1000
    },
    border: {
        width: 7,
        radius: 5
    },
    style: {
        width: {
            max: 500
        },
        name: 'light',
        tip: 'topLeft'
    }
};

function update_embargo_date(event){
    if (jQuery(event.data.from_id).val() == 'embargoedAccess') {
        jQuery(event.data.to_id).show('slow');
    } else {
        jQuery(event.data.to_id).hide('slow');
    }
}

function update_language(event){
    if (jQuery(event.data.from_id).val() != 'eng') {
        jQuery(event.data.to_id).removeAttr("disabled").show('slow');
    } else {
        jQuery(event.data.to_id).attr("disabled", "disabled").hide('slow');
    }
}

function elaborateAjaxGateway(results, textStatus, XMLHttpRequest){
    var errors = results.errors;
    var warnings = results.warnings;
    var addclasses = results.addclasses;
    var delclasses = results.delclasses;
    var hiddens = results.hiddens;
    var appends = results.appends;
    var showns = results.showns;
    var substitutions = results.substitutions;
    var query;
    for (var error in errors) {
        if (errors[error]) {
            jQuery('#error_' + error).html(errors[error]).fadeIn('slow');
        } else {
            jQuery('#error_' + error).fadeOut('slow');
        }
    }
    for (var warning in warnings) {
        if (warnings[warning]) {
            jQuery('#warning_' + warning).html(warnings[warning]).fadeIn('slow');
        } else {
            jQuery('#warning_' + warning).fadeOut('slow');
        }
    }
    for (query in addclasses) {
        jQuery(query).addClass(addclasses[query]);
    }
    for (query in delclasses) {
        jQuery(query).removeClass(delclasses[query]);
    }
    if (hiddens.length > 0) {
        for (query in hiddens) {
            jQuery(hiddens[query]).hide('slow');
        }
    }
    if (appends.length > 0) {
        for (query in appends) {
            jQuery(query).append(appends[query]);
        }
    }
    if (showns.length > 0) {
        for (query in showns) {
            jQuery(showns[query]).show('slow');
        }
    }
    for (query in substitutions) {
        jQuery(query).replaceWith(substitutions[query]);
    }
    return 0;
}

function getPublicationMetadata(publicationid){
    var ret = {};
    jQuery('#body_row_' + publicationid + ' input').each(function(){
        ret[this.id] = this.value;
    });
    jQuery('#body_row_' + publicationid + ' select').each(function(){
        ret[this.id] = this.value;
    });
    jQuery('#body_row_' + publicationid + ' textarea').each(function(){
        ret[this.id] = this.value;
    });
    jQuery('#header_row_' + publicationid + ' input').each(function(){
        ret[this.id] = this.value;
    });
    jQuery('#header_row_' + publicationid + ' select').each(function(){
        ret[this.id] = this.value;
    });
    jQuery('#header_row_' + publicationid + ' textarea').each(function(){
        ret[this.id] = this.value;
    });
    return ret;
}

function object_to_str(o){
    var ret = 'start';
    for (var key in o) {
        ret += key + ' = ' + o[key] + '\n';
    }
    ret += 'end';
    return ret;
}

function ajaxGateway(element, action) {
    var publicationid = element.id.split('_').pop();
    var data = getPublicationMetadata(publicationid);
    data.publicationid = publicationid;
    data.projectid = gProjectid;
    data.action = action;
    data.current_field = element.id;
    jQuery.post(gSite + '/deposit/ajaxgateway', data, elaborateAjaxGateway, "json");
    return 1;
}

function onAjaxError(XHR, textStatus, errorThrown){
  /*
   * Handle Ajax request errors.
   */
  alert('Request completed with status ' + textStatus +
    '\nResult: ' + XHR.responseText +
    '\nError: ' + errorThrown);
}


/* See: http://oranlooney.com/functional-javascript/ */
function Clone() { }
function clone(obj) {
    Clone.prototype = obj;
    return new Clone();
}

/* Initialization */
jQuery(document).ready(function(){
    jQuery('div.OpenAIRE input:text,div.OpenAIRE textarea,div.OpenAIRE select').focusout(function(){
        return ajaxGateway(this, 'verify_field');
    });
    jQuery('div.OpenAIRE select').select(function(){
        return ajaxGateway(this, 'verify_field');
    });
    jQuery('#project').autocomplete({
        source: gSite + "/kb/export?kbname=projects&format=jquery&limit=20&ln=" + gLn,
        focus: function(event, ui) {
            jQuery('#projectid').val(ui.item.label);
            return false;
        },
        select: function(event, ui) {
            jQuery('#project').val(ui.item.label);
            jQuery('#projectid').val(ui.item.value);
            return false;
        }
    }).focus();
    jQuery(function(){
        /* Adapted from <http://jqueryui.com/demos/autocomplete/#multiple> */
        function split(val) {
            return val.split(/\r\n|\r|\n/);
        }
        function extractLast(term) {
            return split(term).pop();
        }

        jQuery('textarea.authors').keydown(function(event) {
            /* Thanks to: http://forum.jquery.com/topic/autocomplete-changing-key-bindings */
            var isOpen = jQuery( this ).autocomplete( "widget" ).is( ":visible" );
            var keyCode = jQuery.ui.keyCode;
            if ( !isOpen && ( event.keyCode == keyCode.UP || event.keyCode == keyCode.DOWN ) ) {
                    event.stopImmediatePropagation();
            }
          }).autocomplete({
            source: function(request, response) {
                // delegate back to autocomplete, but extract the last term
                var publicationid = this.element[0].name; // FIXME: find a better
                // way to retrieve the publicationid!
                var term = extractLast(request.term);
                if (term) {

                    jQuery.getJSON(gSite + "/deposit/authorships", {
                        publicationid: publicationid,
                        term: term
                    }, function(data, status, xhr) {
                        if (data) {
                            response(data);
                        }
                    });
                }
            },
            focus: function(event, ui){
                return false;
            },
            select: function(event, ui) {
                var terms = split(this.value);
                // remove the current input
                terms.pop();
                // add the selected item
                terms.push(ui.item.value);
                this.value = terms.join("\n") + "\n";
                return false;
            }
        });
        jQuery('textarea.keywords').keydown(function(event) {
            /* Thanks to: http://forum.jquery.com/topic/autocomplete-changing-key-bindings */
            var isOpen = jQuery( this ).autocomplete( "widget" ).is( ":visible" );
            var keyCode = jQuery.ui.keyCode;
            if ( !isOpen && ( event.keyCode == keyCode.UP || event.keyCode == keyCode.DOWN ) ) {
                    event.stopImmediatePropagation();
            }
          }).autocomplete({
            source: function(request, response) {
                // delegate back to autocomplete, but extract the last term
                var publicationid = this.element[0].name; // FIXME: find a better
                // way to retrieve the publicationid!
                var term = extractLast(request.term);
                if (term) {

                    jQuery.getJSON(gSite + "/deposit/keywords", {
                        publicationid: publicationid,
                        term: term
                    }, function(data, status, xhr) {
                        if (data) {
                            response(data);
                        }
                    });
                }
            },
            focus: function(event, ui){
                return false;
            },
            select: function(event, ui) {
                var terms = split(this.value);
                // remove the current input
                terms.pop();
                // add the selected item
                terms.push(ui.item.value);
                this.value = terms.join("\n") + "\n";
                return false;
            }
        });
    });
    jQuery('*[title]').qtip(gTipDefault);
    jQuery('div.error').filter(function(){
        return this.textContent == '' || this.textContent == undefined;
    }).hide();
    jQuery('div.warning').filter(function(){
        return this.textContent == '' || this.textContent == undefined;
    }).hide();
    jQuery.datepicker.setDefaults(jQuery.datepicker.regional[gLn]);
    jQuery('span.yesscript').show();
});
