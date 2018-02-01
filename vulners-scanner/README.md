## RUS
**Установка:**
* Скопировать скрипты `git clone ` в `/root/`
* Переместить директорию с ключами `mv -f /root/vulners-scanner/vulners-key /root/ && chmod 600 /root/vulners-scanner/vulners_key*`
* Добавить 2 задания в `/etc/cron.d`:

**check_vulners**
```
# start check vulners daily at 8am
55 7 * * * root bash /root/vulners-scanner/get_vulners_db.sh &> /var/log/get_vulners_db_debug
00 8 * * * root bash /root/vulners-scanner/sendmail.sh &> /var/log/vulners_debug
```
**check_vulners_hourly** 

```
# start check vulners hourly
0 * * * * root bash /root/vulners-scanner/get_vulners_db.sh &> /var/log/get_vulners_db_debug
0 * * * * root python /root/vulners-scanner/vulners_over_ssh_scanner.py &> /var/log/zbx_vulners_debug
```
* Импортировать `Template_App_Vulners_Trap.xml` в **Zabbix**
* Список проверяемых хостов: `hosts`
* Установить необходимые модули для Python ` yum install python-paramiko epel-release python-pip && pip install py-zabbix executor`
* Добавление пользователя для сканирования:
```
useradd vulners-scanner
mkdir -p -m 700 /home/vulners-scanner/.ssh
echo "ssh-rsa XXX vulners-scanner" >> /home/vulners-scanner/.ssh/authorized_keys
chown -R vulners-scanner:vulners-scanner /home/vulners-scanner/
chmod 600 /home/vulners-scanner/.ssh/authorized_keys
echo "vulners-scanner:password" | chpasswd
```

## ENG
