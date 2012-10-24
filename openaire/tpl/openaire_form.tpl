<tr class="header odd" id="header_row_%(id)s">
    <td width="5%%" id="status_%(id)s" rowspan="2" class="%(status)s"><span id="status_msg_%(id)s" class="status_msg">%(collapse_label)s</span></td>
    <td width="40%%" valign="top">
        %(publication_information)s
        <br />
        %(fulltext_information)s
        <br />
    </td>
    <td width="35%%" valign="top">
    	<div class="typebox_%(id)s %(access_rights_classes)s">
	        <img title="%(access_rights_tooltip)s" class="tooltip mandatory" src="%(site)s/img/help.png" /> 
	        <select id="access_rights_%(id)s" name="access_rights_%(id)s" class="access_rights">
	            %(access_rights_options)s
	        </select> <img src="%(site)s/img/asterisk.png" alt="mandatory">
	        <div id="error_access_rights_%(id)s" class="error">%(error_embargo_date_value)s</div>
	        <div id="warning_access_rights_%(id)s" class="warning">%(warning_embargo_date_value)s</div>
	        <div id="embargo_date_container_%(id)s">
	            <img title="%(embargo_date_tooltip)s" class="tooltip mandatory" src="%(site)s/img/help.png"/>
	            <input name="embargo_date_%(id)s" type="text" id="embargo_date_%(id)s" value="%(embargo_date_value)s" size="%(embargo_date_size)s" maxlength="10" class="datepicker" />
	            <div id="error_embargo_date_%(id)s" class="error">%(error_embargo_date_value)s</div>
	            <div id="warning_embargo_date_%(id)s" class="warning">%(warning_embargo_date_value)s</div>
	        </div>
        </div>
    </td>
    <td width="20%%" valign="top">
        <a href="javascript:void(0)" id="edit_metadata_%(id)s"><img src="%(site)s/img/wb-notes.png" alt="%(edit_metadata_label)s"/> <strong>%(edit_metadata_label)s</strong></a><br />
        <a href="%(site)s/deposit?projectid=%(projectid)s&amp;delete=%(id)s&amp;ln=%(ln)s" id="remove_%(id)s"><img src="%(site)s/img/smallbin.gif" /> %(remove_label)s</a>
    </td>
</tr>
<tr class="body even" id="body_row_%(id)s">
    <td colspan="3" valign="top">
        <div id="body_%(id)s" class="body">
            <p><em>%(mandatory_label)s</em></p>
            <fieldset>
                <!--<legend>%(publication_type)s</legend>-->
                <div>
	                <img title="%(publication_type_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
	                <label class="mandatory">%(publication_type_label)s</label>
	                <select name="publication_type_%(id)s" id="publication_type_%(id)s" class="publication_type">
	                        %(publication_type_options)s
	                </select>
	                <div id="error_publication_type_%(id)s" class="error">%(error_publication_type_value)s</div>
	                <div id="warning_publication_type_%(id)s" class="warning">%(warning_publication_type_value)s</div>
                </div>
                <div class="typebox_%(id)s typebox_%(id)s_data">
	                <img title="%(accept_cc0_license_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
	                <input type="checkbox" value="yes" name="accept_cc0_license_%(id)s" id="accept_cc0_license_%(id)s" class="accept_cc0_license" /> %(accept_cc0_license_label)s <a href="http://creativecommons.org/publicdomain/zero/1.0/"><img src="%(site)s/img/cc-zero.png" /></a>
	                <div id="error_accept_cc0_license_%(id)s" class="error">%(error_accept_cc0_license_value)s</div>
	                <div id="warning_accept_cc0_license_%(id)s" class="warning">%(warning_accept_cc0_license_value)s</div>
	            </div>
            </fieldset>
            <fieldset>
                <legend>%(projects_information_label)s</legend>
                <img title="%(projects_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                <label class="mandatory">%(projects_description)s</label>
                %(projects_information)s
                <div id="error_projects_%(id)s" class="error">%(error_projects_value)s</div>
                <div id="warning_projects_%(id)s" class="warning">%(warning_projects_value)s</div>
            </fieldset>
            <div class="clear"></div>
            <fieldset>
                <div>
                    <img title="%(authors_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                    <label for="authors_%(id)s" class="mandatory">%(authors_label)s</label><br />
                    <textarea name="authors_%(id)s" id="authors_%(id)s" cols="60" rows="5" class="authors" placeholder="%(authors_placeholder)s">%(authors_value)s</textarea>
                    
                    <div id="error_authors_%(id)s" class="error">%(error_authors_value)s</div>
                    <div id="warning_authors_%(id)s" class="warning">%(warning_authors_value)s</div>
                </div>
            </fieldset>
            <div class="clear"></div>

            <div class="typebox_%(id)s typebox_%(id)s_thesis">
                <fieldset>
                    <div>
                        <img title="%(supervisors_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                        <label for="supervisors_%(id)s">%(supervisors_label)s</label><br />
                        <textarea name="supervisors_%(id)s" id="supervisors_%(id)s" cols="60" rows="5" class="supervisors" placeholder="%(supervisors_placeholder)s">%(supervisors_value)s</textarea>
                        <div id="error_supervisors_%(id)s" class="error">%(error_supervisors_value)s</div>
                        <div id="warning_supervisors_%(id)s" class="warning">%(warning_supervisors_value)s</div>
                    </div>
                </fieldset>
                <div class="clear"></div>
            </div>

            <fieldset>
                <legend>%(english_language_label)s</legend>
                <div>
                    <img title="%(title_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                    <label for="title_%(id)s" class="mandatory">%(title_label)s
                    </label>
                    <br />
                    <input type="text" name="title_%(id)s" id="title_%(id)s" value="%(title_value)s" size="75" class="title" />
                    <div id="error_title_%(id)s" class="error">%(error_title_value)s</div>
                    <div id="warning_title_%(id)s" class="warning">%(warning_title_value)s</div>
                </div>
                <div>
                    <img title="%(abstract_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                    <label for="abstract_%(id)s" class="mandatory">%(abstract_label)s
                    </label>
                    <br />
                    <textarea name="abstract_%(id)s" id="abstract_%(id)s" cols="60" rows="5" class="abstract">%(abstract_value)s</textarea>
                    <div id="error_abstract_%(id)s" class="error">%(error_abstract_value)s</div>
                    <div id="warning_abstract_%(id)s" class="warning">%(warning_abstract_value)s</div>
                </div>
            </fieldset>
            <fieldset>
                <legend>%(original_language_label)s</legend>
                <div>
                    <img title="%(language_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                    <label for="language_%(id)s" class="mandatory">%(language_label)s
                    </label>
                    <select name="language_%(id)s" id="language_%(id)s" class="language" style="width: 100px">
                        %(language_options)s
                    </select>
                    <div id="error_language_%(id)s" class="error">%(error_language_value)s</div>
                    <div id="warning_language_%(id)s" class="warning">%(warning_language_value)s</div>
                </div>
                <div id="original_language_container_%(id)s">
                    <div>
                        <img title="%(original_title_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                        <label for="original_title_%(id)s">%(original_title_label)s
                        </label>
                        <br />
                        <input type="text" name="original_title_%(id)s" id="original_title_%(id)s" value="%(original_title_value)s" size="75" class="original_title mandatory" />
                        <div id="error_original_title_%(id)s" class="error">%(error_original_title_value)s</div>
                        <div id="warning_original_title_%(id)s" class="warning">%(warning_original_title_value)s</div>
                    </div>
                    <div>
                        <img title="%(original_abstract_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                        <label for="original_abstract_%(id)s">%(original_abstract_label)s
                        </label>
                        <br />
                        <textarea name="original_abstract_%(id)s" id="original_abstract_%(id)s" cols="60" rows="5" class="original_abstract">%(original_abstract_value)s</textarea>
                        <div id="error_original_abstract_%(id)s" class="error">%(error_original_abstract_value)s</div>
                        <div id="warning_original_abstract_%(id)s" class="warning" >%(warning_original_abstract_value)s</div>
                    </div>
                </div>
            </fieldset>
            <div class="clear"></div>
            <fieldset>
                <legend>%(identifiers_information_label)s</legend>
                <div>
                    <img title="%(doi_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                    <label for="doi_%(id)s">%(doi_label)s
                    </label>
                    <br />
                    <input type="text" name="doi_%(id)s" id="doi_%(id)s" value="%(doi_value)s" size="75" class="doi" placeholder="10.1234/foo-bar" pattern="(doi:)?10\.\d+/.*"/>
                    <div id="error_doi_%(id)s" class="error">%(error_doi_value)s</div>
                    <div id="warning_doi_%(id)s" class="warning">%(warning_doi_value)s</div>
                </div>
                <div class="typebox_%(id)s typebox_%(id)s_report typebox_%(id)s_book">
                    <img title="%(isbn_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                    <label for="isbn_%(id)s">%(isbn_label)s
                    </label>
                    <br />
                    <input type="text" name="isbn_%(id)s" id="isbn_%(id)s" value="%(isbn_value)s" size="75" class="isbn" placeholder="e.g. 0-06-251587-X" />
                    <div id="error_isbn_%(id)s" class="error">%(error_isbn_value)s</div>
                    <div id="warning_isbn_%(id)s" class="warning">%(warning_isbn_value)s</div>
                </div>
            </fieldset>
            <div class="clear"></div>
            <fieldset>
                <legend>%(publication_information_label)s</legend>
                <div>
                    <img title="%(publication_date_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                    <label for="publication_date_%(id)s" class="mandatory">%(publication_date_label)s</label>
                    <input name="publication_date_%(id)s" type="text" id="publication_date_%(id)s" value="%(publication_date_value)s" size="10" maxlength="10" class="datepicker" />
                    <div id="error_publication_date_%(id)s" class="error">%(error_publication_date_value)s</div>
                    <div id="warning_publication_date_%(id)s" class="warning">%(warning_publication_date_value)s</div>
                </div>
                <div class="typebox_%(id)s typebox_%(id)s_publishedArticle">
	                <div>
	                    <img title="%(journal_title_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
	                    <label for="journal_title_%(id)s">%(journal_title_label)s
	                    </label>
	                    <br />
	                    <input type="text" name="journal_title_%(id)s" id="journal_title_%(id)s" value="%(journal_title_value)s" size="75" class="journal_title" />
	                    <div id="error_journal_title_%(id)s" class="error">%(error_journal_title_value)s</div>
	                    <div id="warning_journal_title_%(id)s" class="warning">%(warning_journal_title_value)s</div>
	                </div>
	                <div>
	                    <img title="%(volume_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
	                    <label for="volume_%(id)s">%(volume_label)s</label>
	                    <input name="volume_%(id)s" type="text" id="volume_%(id)s" value="%(volume_value)s" size="4" class="volume" />
	                    <img title="%(issue_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
	                    <label for="issue_%(id)s">%(issue_label)s</label>
	                    <input name="issue_%(id)s" type="text" id="issue_%(id)s" value="%(issue_value)s" size="4" class="issue" />
	                    <img title="%(pages_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
	                    <label for="pages_%(id)s">%(pages_label)s</label>
	                    <input name="pages_%(id)s" type="text" id="pages_%(id)s" value="%(pages_value)s" size="8" class="pages" />
	                    <div id="error_volume_%(id)s" class="error">%(error_volume_value)s</div>
	                    <div id="warning_volume_%(id)s" class="warning">%(warning_volume_value)s</div>
	                    <div id="error_issue_%(id)s" class="error">%(error_issue_value)s</div>
	                    <div id="warning_issue_%(id)s" class="warning">%(warning_issue_value)s</div>
	                    <div id="error_pages_%(id)s" class="error">%(error_pages_value)s</div>
	                    <div id="warning_pages_%(id)s" class="warning">%(warning_pages_value)s</div>
	                </div>
	            </div>
                <div class="typebox_%(id)s typebox_%(id)s_report">
                    <img title="%(report_type_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                    <label for="report_type_%(id)s" class="mandatory">%(report_type_label)s</label>
                    <select name="report_type_%(id)s" id="report_type_%(id)s" class="report_type">
                        %(report_type_options)s
                    </select>
                    <br />
                    <div id="error_report_type_%(id)s" class="error">%(error_report_type_value)s</div>
                    <div id="warning_report_type_%(id)s" class="warning">%(warning_report_type_value)s</div>
                </div>
                <div class="typebox_%(id)s typebox_%(id)s_thesis">
                    <img title="%(thesis_type_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                    <label for="thesis_type_%(id)s" class="mandatory">%(thesis_type_label)s</label>
                    <select name="thesis_type_%(id)s" id="thesis_type_%(id)s" class="thesis_type">
                        %(thesis_type_options)s
                    </select>
                    <br />
                    <div id="error_thesis_type_%(id)s" class="error">%(error_thesis_type_value)s</div>
                    <div id="warning_thesis_type_%(id)s" class="warning">%(warning_thesis_type_value)s</div>
                </div>
                <div class="typebox_%(id)s typebox_%(id)s_thesis">
                    <img title="%(university_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                    <label for="university_%(id)s" class="mandatory">%(university_label)s</label>
                    <input type="text" name="university_%(id)s" id="university_%(id)s" value="%(university_value)s" size="50" class="university" />
                    <br />
                    <div id="error_university_%(id)s" class="error">%(error_university_value)s</div>
                    <div id="warning_university_%(id)s" class="warning">%(warning_university_value)s</div>
                </div>
                <div class="typebox_%(id)s typebox_%(id)s_report typebox_%(id)s_thesis typebox_%(id)s_book">
                    <img title="%(publisher_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                    <label for="publisher_%(id)s">%(publisher_label)s</label>
                    <input type="text" name="publisher_%(id)s" id="publisher_%(id)s" value="%(publisher_value)s" size="15" class="publisher" />
                    <img title="%(place_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                    <label for="place_%(id)s">%(place_label)s</label>
                    <input type="text" name="place_%(id)s" id="place_%(id)s" value="%(place_value)s" size="15" class="place" />
                    <br />
                    <div id="error_publisher_%(id)s" class="error">%(error_publisher_value)s</div>
                    <div id="warning_publisher_%(id)s" class="warning">%(warning_publisher_value)s</div>
                    <div id="error_place_%(id)s" class="error">%(error_place_value)s</div>
                    <div id="warning_place_%(id)s" class="warning">%(warning_place_value)s</div>
                </div>
                <div class="typebox_%(id)s typebox_%(id)s_report typebox_%(id)s_thesis typebox_%(id)s_book">
                    <img title="%(report_pages_no_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                    <label for="report_pages_no_%(id)s">%(report_pages_no_label)s</label>
                    <input type="text" name="report_pages_no_%(id)s" id="report_pages_no_%(id)s" value="%(report_pages_no_value)s" size="4" class="report_pages_no" />
                    <br />
                    <div id="error_report_pages_no_%(id)s" class="error">%(error_report_pages_no_value)s</div>
                    <div id="warning_report_pages_no_%(id)s" class="warning">%(warning_report_pages_no_value)s</div>
                </div>
                <div class="typebox_%(id)s typebox_%(id)s_report">
                    <img title="%(extra_report_numbers_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                    <label for="extra_report_numbers_%(id)s">%(extra_report_numbers_label)s</label>
                    <br />
                    <textarea name="extra_report_numbers_%(id)s" id="extra_report_numbers_%(id)s" cols="60" rows="5" class="extra_report_numbers">%(extra_report_numbers_value)s</textarea>
                    <div id="error_extra_report_numbers_%(id)s" class="error">%(error_extra_report_numbers_value)s</div>
                    <div id="warning_extra_report_numbers_%(id)s" class="warning">%(warning_extra_report_numbers_value)s</div>
                </div>
                <div class="typebox_%(id)s typebox_%(id)s_data">
                    <img title="%(dataset_publisher_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                    <label for="dataset_publisher_%(id)s">%(dataset_publisher_label)s</label>
                    <input type="text" name="dataset_publisher_%(id)s" id="dataset_publisher_%(id)s" value="%(dataset_publisher_value)s" size="50" class="dataset_publisher" />
                    <br />
                    <div id="error_dataset_publisher_%(id)s" class="error">%(error_dataset_publisher_value)s</div>
                    <div id="warning_dataset_publisher_%(id)s" class="warning">%(warning_dataset_publisher_value)s</div>
                </div>
            </fieldset>
            <fieldset>
                <legend>%(other_information_label)s</legend>
                <div>
                    <img title="%(keywords_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                    <label for="keywords_%(id)s">%(keywords_label)s
                    </label>
                    <br />
                    <textarea name="keywords_%(id)s" id="keywords_%(id)s" cols="60" rows="5" class="keywords">%(keywords_value)s</textarea>
                    <div id="error_keywords_%(id)s" class="error">%(error_keywords_value)s</div>
                    <div id="warning_keywords_%(id)s" class="warning">%(warning_keywords_value)s</div>
                </div>
                <div>
                    <img title="%(notes_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                    <label for="notes_%(id)s">%(notes_label)s
                    </label>
                    <br />
                    <textarea name="notes_%(id)s" id="notes_%(id)s" cols="60" rows="5" class="notes">%(notes_value)s</textarea>
                    <div id="error_notes_%(id)s" class="error">%(error_notes_value)s</div>
                    <div id="warning_notes_%(id)s" class="warning">%(warning_notes_value)s</div>
                </div>
            </fieldset>
            <div class="typebox_%(id)s typebox_%(id)s_data">
                <fieldset>
                    <legend>%(related_publications_legend_label)s</legend>
                       <div>
                            <img title="%(related_publications_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                            <label for="related_publications_%(id)s">%(related_publications_label)s</label>
                            <br />
                            <textarea name="related_publications_%(id)s" id="related_publications_%(id)s" cols="60" rows="5" class="related_publications" placeholder="10.1234/foo.bar (one per line)">%(related_publications_value)s</textarea>
                            <div id="error_related_publications_%(id)s" class="error">%(error_related_publications_value)s</div>
                            <div id="warning_related_publications_%(id)s" class="warning">%(warning_related_publications_value)s</div>
                        </div>
                </fieldset>
            </div>
            <div class="typebox_%(id)s typebox_%(id)s_book typebox_%(id)s_report typebox_%(id)s_publishedArticle typebox_%(id)s_thesis">
                <fieldset>
                    <legend>%(related_datasets_legend_label)s</legend>
                       <div>
                            <img title="%(related_datasets_tooltip)s" class="tooltip" src="%(site)s/img/help.png" />
                            <label for="related_datasets_%(id)s">%(related_datasets_label)s</label>
                            <br />
                            <textarea name="related_datasets_%(id)s" id="related_datasets_%(id)s" cols="60" rows="5" class="related_datasets" placeholder="10.1234/foo.bar (one per line)">%(related_datasets_value)s</textarea>
                            <div id="error_related_datasets_%(id)s" class="error">%(error_related_datasets_value)s</div>
                            <div id="warning_related_datasets_%(id)s" class="warning">%(warning_related_datasets_value)s</div>
                        </div>
                </fieldset>
            </div>
            <div class="clear"></div>
            <input type="submit" value="%(save_label)s" name="save_%(id)s" id="save_%(id)s"/><input type="submit" value="%(submit_label)s" name="submit_%(id)s" id="submit_%(id)s"/>
        </div>
    </td>
</tr>
<script type="text/javascript">// <![CDATA[
    jQuery(document).ready(function(){
        /* Show/hide access rights */
        jQuery('#access_rights_%(id)s').bind('change', {
            from_id: '#access_rights_%(id)s',
            to_id: '#embargo_date_container_%(id)s'
        }, update_embargo_date);
        jQuery('#access_rights_%(id)s').trigger('change');
        
        /* Show/hide original language box */
        jQuery('#language_%(id)s').bind('change', {
            from_id: '#language_%(id)s',
            to_id: '#original_language_container_%(id)s'
        }, update_language);
        update_language({
            data: {
                from_id: '#language_%(id)s',
                to_id: '#original_language_container_%(id)s'
            }
        });
        
        /* Show/hide specific information box */
        jQuery('#publication_type_%(id)s').bind('change', {
            from_id: '#publication_type_%(id)s',
            to_class_prefix: '.typebox_%(id)s_',
            to_class: '.typebox_%(id)s'
        }, update_specific_information);
        
        jQuery('#publication_type_%(id)s').trigger('change');
		
        
        jQuery('#save_%(id)s').click(function(event){
            var element = this;
            ajaxGateway(element, 'save');
            event.preventDefault();
            return 0;
        });
        jQuery('#submit_%(id)s').click(function(event){
            var element = this;
            ajaxGateway(element, 'submit');
            event.preventDefault();
            return 0;
        });
        jQuery('#remove_%(id)s').click(function(){
            return confirm("%(remove_confirm)s");
        });
        jQuery('#edit_metadata_%(id)s,#status_%(id)s').click(function(){
            jQuery('#body_%(id)s').toggle();
            if(jQuery('#status_msg_%(id)s').html() == "%(collapse_label)s") {
                jQuery('#status_msg_%(id)s').html("%(expand_label)s")
            } else {
                jQuery('#status_msg_%(id)s').html("%(collapse_label)s")
            }
            return false;
        });
        jQuery('#journal_title_%(id)s').autocomplete({
            source: "%(site)s/kb/export?kbname=journal_name&amp;format=jquery&amp;ln=%(ln)s&amp;limit=100"
        });
//         jQuery('#body_%(id)s').hide();
    });
// ]]></script>
