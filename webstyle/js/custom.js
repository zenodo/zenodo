var alert_template = Hogan.compile('<div class="alert alert-{{status}}"><button type="button" class="close" data-dismiss="alert">&times;</button>{{message}}</div>');
var tag_templates = {
    'funding_source' : Hogan.compile('<li class="alert alert-info tag" data-tag-id="{{grant_agreement_number}}"><button type="button" class="close" data-dismiss="alert">&times;</button>{{label}}</li>'),
    'collections' : Hogan.compile('<li class="alert alert-info tag" data-tag-id="{{value}}"><button type="button" class="close" data-dismiss="alert">&times;</button>{{label}}</li>')
};


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

    /* Open/close menu on hoover */
    $('ul.nav li.dropdown').hover(function() {
        $(this).find('.dropdown-menu').stop(true, true).show();
        $(this).addClass('open');
    }, function() {
        $(this).find('.dropdown-menu').stop(true, true).hide();
        $(this).removeClass('open');
    });
});

function webdeposit_input_error_check(selector, url) {
    $(selector).change( function() {
        name = this.name;
        value = this.value;
        $.getJSON(url, {
            field: name,
            value: value
        }, function(data) {
            if (data.error == 1) {
            errorMsg = data.error_message;
                $('#error-'+name).html(errorMsg);
                $('.field-'+name).addClass("error");
                $('#error-'+name).show();
            } else {
                $('#error-'+name).hide();
                $('.field-'+name).removeClass("error");
            }
        });
        return false;
    });
}

var date_options = {
    format: 'yyyy-mm-dd',
    weekStart: 1,
    autoclose: true,
    todayBtn: "linked",
    todayHighlight: true,
    keyboardNavigation: true
};

function webdeposit_datepicker(selector){
    $(selector).addClass("input-small");
    $(selector).datepicker(date_options);
}

function split(val) {
    return val.split(/\r\n|\r|\n/);
}

function extractLast(term) {
    return split(term).pop();
}

var autocomplete_tag_fields = [];

function webdeposit_autocomplete(selector, remote_url, with_tags) {
    $('input.'+selector).autocomplete({
        source: function( request, response ) {
            $.ajax({
                url: remote_url,
                dataType: "json",
                data: {
                    term: request.term
                },
                success: function( data ) {
                    if(data){
                        return response(data);
                    }
                }
            });
        },
        select: function( e, ui ) {
            if (with_tags) {
                existing_ids = $.map( $('#'+selector+'_values li'), function(e){ return $(e).data('tagId').toString(); } );
                if(existing_ids.indexOf(ui.item.value) == -1){
                    tag_template = tag_templates[selector];
                    $('#'+selector+'_values ul').append(tag_template.render(ui.item));
                }
                $('input.'+selector).val("");
            }
            e.preventDefault();
        }
    });
    if (with_tags) {
        autocomplete_tag_fields.push(selector);
    }
    $('#'+selector+'_values ul').sortable();
    $('#'+selector+'_values ul').disableSelection();
}

/* Adapted from <http://jqueryui.com/demos/autocomplete/#multiple> */
function webdeposit_autocomplete_textarea(selector, remote_url) {
    $('.'+selector).keydown(function(event) {
        /* Thanks to: http://forum.jquery.com/topic/autocomplete-changing-key-bindings */
        var isOpen = jQuery( this ).autocomplete( "widget" ).is( ":visible" );
        var keyCode = jQuery.ui.keyCode;
        if ( !isOpen && ( event.keyCode == keyCode.UP || event.keyCode == keyCode.DOWN ) ) {
            event.stopImmediatePropagation();
        }
    }).autocomplete({
        source: function(request, response) {
            term = extractLast(request.term);
            if (term) {
                $.ajax({
                    url: remote_url,
                    dataType: "json",
                    data: {
                        term: term
                    },
                    success: function( data ) {
                        if(data) {
                            response(data);
                        }
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
}

// Typeahead.js autocomplete
// function webdeposit_autocomplete(selector, prefetch_url, remote_url) {
//     $('input.'+selector).typeahead({
//         name: selector,
//         prefetch: prefetch_url,
//         remote: remote_url
//     });
// }

function webdeposit_field_enabler(selector, mapping, trigger_all) {
    $(selector).change(function(e){
        if($(this).val() in mapping){
            fields_map = mapping[$(this).val()];
            fields_map[0].forEach(function (f, idx, arr){
                $('#'+f).removeAttr('disabled');
                $('label[for='+f+']').removeClass('muted');
            });
            fields_map[1].forEach(function (f, idx, arr){
                $('#'+f).attr('disabled','');
                $('label[for='+f+']').addClass('muted');
            });
        }
    });
    if( trigger_all ){
        $(selector).trigger('change');
    }
    $(selector + ':checked').trigger('change');
}

function webdeposit_submit_button(selector, form_selector) {
    $(selector).click(function(e){
        autocomplete_tag_fields.forEach(function(e){
            $("input."+e).css("color","white");
            $("input."+e).val(($.map( $('#'+e+'_values li'), function(e){ return $(e).data('tagId').toString(); } )).toString());
        });
        $(form_selector).submit();
        e.preventDefault();
    });
}

function webdeposit_save_button(selector, form_selector, message_selector, url) {
    $(selector).click(function(e){
        $(".state-success").hide();
        $(".state-failure").hide();
        $(".state-danger").hide();
        $(".loader").addClass("loading");
        // Compute value of tag autocomplete fields
        var textcolor = null;
        autocomplete_tag_fields.forEach(function(e){
            textcolor = $("input."+e).css("color");
            $("input."+e).css("color","white");
            $("input."+e).val(($.map( $('#'+e+'_values li'), function(e){ return $(e).data('tagId').toString(); } )).toString());
        });
        $.ajax({
            url: url,
            type: 'POST',
            cache: false,
            data: $(form_selector).serialize(),
            dataType: 'json'
        }).done(function(data) {
            if(data.status == 'success' ){
                // Hide all errors
                $(form_selector).serializeArray().forEach(function(field){
                    $('#error-'+field['name']).hide();
                    $('.field-'+field['name']).removeClass("error");
                });
                // Show success message
                $(message_selector).html(alert_template.render({status: data.status, message: data.form }));
                $(".state-success").show();
            } else {
                for(var f in data.fields) {
                    if(data.fields[f]){
                        $('#error-'+f).html(data.fields[f]);
                        $('.field-'+f).addClass("error");
                        $('#error-'+f).show();
                    } else {
                        $('.field-'+f).removeClass("error");
                        $('#error-'+f).hide();
                    }
                }
                $(message_selector).html(alert_template.render({status: data.status, message: data.form }));
                $(".state-failure").show();
            }
            $(".loader").removeClass("loading");
        }).fail(function(data) {
            $(message_selector).html(alert_template.render({status: 'danger', 'message': 'The form could not be saved, due to communication problem with the server. Please try to reload your browser.' }));
            $(".loader").removeClass("loading");
            $(".state-danger").show();
        });
        // Resetvalue of tag autocomplete fields (can be done as soon as request have been made)
        autocomplete_tag_fields.forEach(function(e){
            $("input."+e).val("");
            $("input."+e).css("color",textcolor);
        });
        e.preventDefault();
    });
}