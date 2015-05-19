### Not sure what to do here yet. Looks like in Ubuntu they append or somehow send the app.ini file into /etc/environment.
### How do I do the same thing on FreeBSD?
### Linux systems use /etc/environment
### FreeBSD uses /etc/login.conf
###
# source /etc/environment
cd `dirname "$0"`
source ../virtualenv/bin/activate
eval $@