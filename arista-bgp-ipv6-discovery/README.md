# RUS
## Скрипт использует низкоуровневое обнаружение zabbix для сесссий Arista BGP IPv6.

### Как использовать (Zabbix 3.4+):

* Положить скрипт `arista.bgp.discovery` в дирректорию `/usr/lib/zabbix/externalscripts/`
* `chmod +x /usr/lib/zabbix/externalscripts/arista.bgp.discovery`
* Импортировать шаблон `Template_SNMP_v3_ARISTA_BGP_IPv6_Session.xml` в Zabbix
* Изменить макрос в шаблоне на учетные данные от устройств Arista snmpv3
* Добавить необходимые хосты в шаблон

# ENG
## This script use zabbix low level discovery for Arista BGP IPv6 Sessions.

### How to use (Zabbix 3.4+):

* Put `arista.bgp.discovery` in to `/usr/lib/zabbix/externalscripts/`
* `chmod +x /usr/lib/zabbix/externalscripts/arista.bgp.discovery`
* Import template `Template_SNMP_v3_ARISTA_BGP_IPv6_Session.xml` in to Zabbix
* Change macro in template about arista device snmpv3 credentials
* Add hosts in to template


### MIB's require:
`ARISTA-BGP4V2-MIB`
