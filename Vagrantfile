# This file is part of ZENODO.
# Copyright (C) 2014 CERN.
#
# ZENODO is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ZENODO is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

$script = <<SCRIPT

echo I am provisioning...

wget https://raw.githubusercontent.com/bouzlibop/invenio-devscripts/zenodo-kickstart/invenio2-kickstart
chmod u+x ./invenio2-kickstart

CFG_INVENIO2_REPOSITORY_GENERAL="git://github.com/zenodo/invenio" \
CFG_INVENIO2_REPOSITORY_OVERLAY="git://github.com/zenodo/zenodo" \
CFG_INVENIO2_REPOSITORY_GENERAL_BRANCH="pu-zenodo" \
CFG_INVENIO2_REPOSITORY_OVERLAY_BRANCH="master" \
CFG_INVENIO2_VIRTUAL_ENV=zenodo \
CFG_INVENIO2_DATABASE_USER=zenodo \
CFG_INVENIO2_DATABASE_NAME=zenodo \
CFG_INVENIO2_DEMOSITE_POPULATE="-f zenodo/testsuite/demo_zenodo_record_marc_data.xml \
                                -e force-recids" \
./invenio2-kickstart --yes-i-know --yes-i-really-know
SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = "trusty64"
  config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"
  config.vm.hostname = 'localhost.localdomain'
  config.vm.network :forwarded_port, host: 8080, guest: 8080
  config.vm.network :forwarded_port, host: 8443, guest: 8443
  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--memory", "2048"]
    vb.customize ["modifyvm", :id, "--cpus", 2]
  end
  config.vm.provision "shell" do |s|
    s.inline = $script
    s.privileged = false
  end
end