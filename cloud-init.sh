#! /bin/bash

yum -y install python-virtualenv @development git

cd /tmp
git clone https://github.com/blhughes/ML4T
cd ML4T
virtualenv /tmp/env
source /tmp/env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
