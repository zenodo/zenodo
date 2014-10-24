$script = <<SCRIPT

echo I am provisioning...

wget https://raw.githubusercontent.com/bouzlibop/invenio-devscripts/zenodo-kickstart/invenio2-kickstart
chmod u+x ./invenio2-kickstart

CFG_INVENIO2_REPOSITORY_GENERAL="git://github.com/zenodo/invenio-op" \
CFG_INVENIO2_REPOSITORY_OVERLAY="git://github.com/zenodo/zenodo" \
CFG_INVENIO2_REPOSITORY_GENERAL_BRANCH="pu-zenodo" \
CFG_INVENIO2_REPOSITORY_OVERLAY_BRANCH="next" \
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