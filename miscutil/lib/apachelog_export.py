#!/usr/bin/env python
## This file is part of Invenio.
## Copyright (C) 2012 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
Generate a filtered Apache log for external partners.
"""

import sys
import re
from invenio.intbitset import intbitset
import urlparse
import pytz
import os
from md5 import md5

## Generate filtered apache logs from OpenAIRE with:
## $ cd /opt/invenio/var/log
## $ cat apache.log  apache-ssl.log | grep "GET /record/" | grep 200 | gzip > ~/eu.log.gz

## Generate this locally to OpenAIRE with:
from invenio.search_engine import get_collection_reclist, CFG_SITE_NAME
eu_recids = get_collection_reclist(CFG_SITE_NAME)

#eu_recids = intbitset(eu_recids = [9, 10, 19, 23, 24, 25, 26, 773, 774, 778, 779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790, 791, 792, 793, 794, 795, 796, 799, 800, 802, 803, 804, 805, 806, 808, 809, 810, 811, 812, 813, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826, 828, 829, 830, 832, 834, 835, 836, 837, 838, 839, 840, 841, 842, 843, 844, 845, 846, 847, 848, 849, 850, 851, 858, 861, 875, 877, 878, 879, 882, 884, 885, 887, 888, 889, 890, 891, 892, 893, 894, 899, 900, 901, 902, 903, 905, 906, 907, 912, 913, 914, 915, 923, 925, 928, 930, 931, 932, 934])

## This are from CDS
#eu_recids = intbitset([1111467, 1119156, 1119304, 1119305, 1123073, 1131840, 1150815, 1152380, 1153910, 1154457, 1161069, 1165141, 1166365, 1171145, 1171956, 1172330, 1174720, 1174799, 1176934, 1177572, 1178778, 1178965, 1179056, 1179975, 1180629, 1180882, 1181684, 1183307, 1185309, 1186606, 1191601, 1192007, 1194234, 1194627, 1194889, 1194911, 1195998, 1198185, 1198199, 1198803, 1199128, 1201615, 1202603, 1204323, 1204596, 1205042, 1205627, 1206034, 1206388, 1207015, 1207269, 1207509, 1208557, 1209236, 1209302, 1209573, 1210107, 1210369, 1210586, 1210726, 1211321, 1211333, 1212045, 1212628, 1212647, 1212816, 1212901, 1213091, 1213474, 1213664, 1213885, 1213943, 1213965, 1214312, 1214514, 1214626, 1214945, 1215300, 1215671, 1215675, 1216010, 1216172, 1216173, 1216174, 1216175, 1216216, 1216493, 1216578, 1216643, 1217471, 1217703, 1217803, 1217852, 1220800, 1221038, 1221231, 1221713, 1221914, 1221916, 1221919, 1222486, 1222694, 1222700, 1222838, 1223191, 1223198, 1223541, 1223722, 1223846, 1224489, 1224652,
#1224810, 1225128, 1225650, 1225729, 1225965, 1226309, 1226355, 1226551, 1226713, 1226918, 1227094, 1227133, 1227326, 1227792, 1228022, 1228452, 1228934, 1229318, 1229332, 1229356, 1229432, 1229434, 1229530, 1229531, 1229574, 1229575, 1229750, 1229994, 1230077, 1230105, 1230307, 1230376, 1230425, 1230503, 1230736, 1230755, 1230960, 1231305, 1231387, 1231747, 1231901, 1233463, 1233755, 1233863, 1234547, 1234835, 1234922, 1234924, 1234925, 1234926, 1234929, 1235127, 1235128, 1235143, 1235144, 1235145, 1235172, 1235198, 1235259, 1235329, 1235339, 1235904, 1236534, 1236897, 1236925, 1236947, 1237190, 1237309, 1237584, 1237832, 1238451, 1238573, 1239851, 1241005, 1241307, 1241907, 1242058, 1242081, 1242085, 1242526, 1243614, 1243709, 1243710, 1244371, 1244638, 1244718, 1244731, 1246307, 1246557, 1246569, 1246962, 1247395, 1247837, 1248317, 1248563, 1248581, 1248817, 1249009, 1249090, 1249240, 1249428, 1249579, 1249582, 1249711, 1254335, 1254934, 1255033, 1255127, 1255623, 1255958, 1256429, 1256433, 1256515,
#1257430, 1257907, 1258002, 1258154, 1259059, 1259461, 1259591, 1260389, 1260500, 1260579, 1260911, 1260933, 1260943, 1260944, 1260959, 1261330, 1262406, 1262655, 1262878, 1262879, 1262925, 1263511, 1263531, 1264059, 1264268, 1264540, 1264877, 1265038, 1265283, 1265490, 1265837, 1266225, 1266302, 1266406, 1266466, 1266467, 1266797, 1266811, 1267065, 1267078, 1267205, 1267609, 1268099, 1268268, 1268371, 1268394, 1268418, 1268609, 1268772, 1268841, 1269002, 1269265, 1269520, 1269604, 1269752, 1270074, 1270216, 1270325, 1270869, 1271225, 1271829, 1272125, 1272396, 1272477, 1272489, 1272590, 1272628, 1273034, 1273170, 1273211, 1273270, 1273946, 1274170, 1274383, 1274519, 1274659, 1275064, 1275577, 1275587, 1275594, 1275738, 1276020, 1276432, 1276808, 1276861, 1277106, 1277305, 1277454, 1277487, 1277731, 1277830, 1277882, 1277959, 1278031, 1278512, 1279407, 1280616, 1280784, 1280892, 1280951, 1281726, 1281730, 1282194, 1282250, 1282556, 1282605, 1283386, 1283555, 1284223, 1284800, 1285770, 1287375, 1288209,
#1288422, 1289343, 1289612, 1289614, 1289851, 1290019, 1290126, 1291833, 1292549, 1292739, 1293002, 1293698, 1293904, 1294205, 1295863, 1296038, 1296499, 1297362, 1297895, 1297976, 1297977, 1298178, 1298497, 1298507, 1299652, 1300674, 1301014, 1301331, 1301701, 1302208, 1303738, 1303855, 1303952, 1304543, 1304871, 1304875, 1306249, 1307104, 1307421, 1308076, 1310283, 1310886, 1313619, 1313622, 1313681, 1313970, 1314843, 1316237, 1316543, 1317585, 1317804, 1322393, 1323250, 1323908, 1324061, 1324645, 1325254, 1328761, 1328841, 1330864, 1331909, 1334625, 1335312, 1335824, 1336088, 1337830, 1340534, 1340535, 1341481, 1341768, 1342827, 1342828, 1343468, 1343469, 1343470, 1343471, 1343472, 1343880, 1344476, 1345361, 1347544, 1348674, 1349292, 1350832, 1351200, 1351430, 1351551, 1351789, 1352083, 1352136, 1352694, 1352711, 1352765, 1359203, 1385890, 1407211, 1423019, 1428133, 1428908, 1428910, 1436135, 1436386, 1439010, 1443465, 1447061, 1448194, 1449781, 1449803, 1449805, 1449806])

## 128.141.95.175 - - [04/May/2012:15:47:35 +0200] "GET /record/878?ln=en HTTP/1.1" 200 5647 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.41 Safari/536.5"
RE_PATH = re.compile(r"^/record/(?P<recid>\d+)(/(files/(?P<filename>.+\.\w+))?)?$")

_CFG_SALT = None
_CFG_SALT_FILE = os.path.join('.', 'salt.txt')
def get_salt():
    global _CFG_SALT
    if _CFG_SALT:
        return _CFG_SALT
    if os.path.exists(_CFG_SALT_FILE):
        _CFG_SALT = open(_CFG_SALT_FILE).read()
        return _CFG_SALT
    import uuid
    _CFG_SALT = uuid.uuid4()
    open(_CFG_SALT_FILE, "w").write(str(_CFG_SALT))
    return _CFG_SALT

def salt_obfuscate_ip_address(ip):
    return md5(ip + get_salt()).hexdigest()

def format_requester_identifier(ip):
    return "data:,%s" % salt_obfuscate_ip_address(ip)

def format_c_class_subnet(ip):
    subnet = '.'.join(ip.split('.')[:3] + ["0"])
    return "data:,%s" % subnet


utctz = pytz.timezone("UTC")
cerntz = pytz.timezone("Europe/Zurich")

for line in sys.stdin:
    tokens = line.strip().split()
    if tokens[8] != "200":
        continue
    url = tokens[6] ## /record/878?ln=en
    path = urlparse.urlparse(url)[2] ## /record/878
    ip = tokens[0] ## 128.141.95.175
    g = RE_PATH.match(path)
    if g:
        filename = g.group('filename')
        recid = int(g.group('recid'))
        try:
            if recid not in eu_recids:
                continue
        except OverflowError:
            continue
    else:
        continue
    date = (' '.join(tokens[3:5]))[1:-1] ## [04/May/2012:15:47:35 +0200]
    original_date = str(date)
    date = pytz.datetime.datetime.strptime(date.split()[0], "%d/%b/%Y:%H:%M:%S")
    date = cerntz.localize(date)
    date = date.astimezone(utctz)
    date = utctz.normalize(date)
    date = date.isoformat()
    referer = tokens[10][1:-1]
    agent = ' '.join(tokens[11:])[1:-1] ## Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.41 Safari/536.5"
    action = filename and "DOWNLOAD" or "SPLASHPAGE"
    oaiid = "oai:openaire.cern.ch:%s" % recid
    print '\t'.join([oaiid, action, format_requester_identifier(ip), format_c_class_subnet(ip), referer, date, agent])
