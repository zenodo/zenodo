
<div class="well">
    <h4>Export</h4>
    <a href="{{url_for('record.metadata', recid=bfo.recID, of='hx')}}">BibTeX</a>,
    <a href="{{url_for('record.metadata', recid=bfo.recID, of='dcite3')}}">DataCite</a>,
    <a href="{{url_for('record.metadata', recid=bfo.recID, of='xd')}}">DC</a>,
    <a href="{{url_for('record.metadata', recid=bfo.recID, of='xe')}}">EndNote</a>,
    <a href="{{url_for('record.metadata', recid=bfo.recID, of='xn')}}">NLM</a>,
    <a href="{{url_for('record.metadata', recid=bfo.recID, of='xw')}}">RefWorks</a></li>
    <a href="{{url_for('record.metadata', recid=bfo.recID, of='hm')}}">MARC</a>,
    <a href="{{url_for('record.metadata', recid=bfo.recID, of='xm')}}">MARCXML</a>
</div>
