## This script use zabbix low level discovery Arista BGP IPv6 Sessions.

### How to use (Zabbix 3.4+):

* Put `arista.bgp.discovery` in to `/usr/lib/zabbix/externalscripts/`
* `chmod +x /usr/lib/zabbix/externalscripts/arista.bgp.discovery`
* Import `Template_SNMP_v3_ARISTA_BGP_IPv6_Session.xml` in to Zabbix
* Change macro in template about arista device snmpv3 credentials
* Add hosts in to template
