from invenio.search_engine import search_pattern, get_fieldvalues
from invenio.bibrecord import record_add_field, record_xml_output
from invenio.webuser import collect_user_info, get_uid_from_email

print "<collection>"
recids = search_pattern(p="0->Z", f="8560_f")
for recid in recids:
    rec = {}
    record_add_field(rec, "001",  controlfield_value=str(recid))
    email = get_fieldvalues(recid, "8560_f")[0]
    if "<" in email:
        email = email.split()[-1][1:-1].strip()
    user_info = collect_user_info(get_uid_from_email(email))
    name = user_info.get("external_fullname", user_info.get("nickname", ""))
    if name.strip():
            email = "%s <%s>" % (name.strip(), email)
    external_id = user_info.get("external_id", "")
    record_add_field(rec, '856', ind1='0', subfields=[('f', email), ('i', external_id)])
    print record_xml_output(rec)
print "</collection>"
