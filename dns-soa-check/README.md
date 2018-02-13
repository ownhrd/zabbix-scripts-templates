**Install:**

* Скопировать `*.conf` в `/etc/zabbix/zabbix_agentd.d`
* Скопировать `bind-stats.py` в `/usr/local/bin/`
* Скопировать `check_soa` в `/usr/local/bin/`
* Импортировать `Template_App_DNS_SOA_Check_Active.xml` и `Template_App_DNS-bind_Service_Active.xml` в **Zabbix**
* Скомпилировать модуль для **SELinux** из `libzbxsystemd.te` (если нет, то установить пакет: `yum -y install policycoreutils-python`)

```
checkmodule -M -m -o libzbxsystemd.mod libzbxsystemd.te
semodule_package -o libzbxsystemd.pp -m libzbxsystemd.mod

******************** IMPORTANT ***********************

In order to load this newly created policy package into the kernel,
you are required to execute

semodule -i libzbxsystemd.pp
```

* Перезапустить сервис: `systemctl restart zabbix-agent`

* При включенной системе безопасности SELinux наблюдается проблема с запуском агента Zabbix. Проблема с запуском выражается в ошибке: `` cannot set resource limit: [13] Permission denied `` 

* Для устранения проблемы создайте новые правила SELinux на основе заблокированных источников данных:

```
cat /var/log/audit/audit.log | grep zabbix_agentd | grep denied | audit2allow -M zabbix_agent_setrlimit 
semodule -i zabbix_agent_setrlimit.pp 
systemctl start zabbix-agent
```
