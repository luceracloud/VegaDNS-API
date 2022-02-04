#!/bin/sh

# Remove previous access token if it exists
ACCESS_TOKEN=`stat -nf "%N" /root/.vegadns-access-token-default-* 2>&1`
[ $? -eq 0 -a -e "$ACCESS_TOKEN" ] && rm -f $ACCESS_TOKEN

TINYDNS_ROOT=/usr/local/tinydns/root
vdns export > $TINYDNS_ROOT/data.new

if [ -r $TINYDNS_ROOT/data ];
then
  C_MD5=`md5 -q $TINYDNS_ROOT/data`
  N_MD5=`md5 -q $TINYDNS_ROOT/data.new`

  if [ "$C_MD5" = "$N_MD5" ];
  then
    rm -f $TINYDNS_ROOT/data.new
    exit 0
  fi
fi

mv $TINYDNS_ROOT/data.new $TINYDNS_ROOT/data
make -C $TINYDNS_ROOT >/dev/null 2>&1
if [ $? -ne 0 ];
then
  echo Failed to Instatiate new tinydns data file.
  exit 1
fi

for _host in 172.23.99.158 172.23.90.200 172.23.90.201 172.23.72.157 172.23.72.158
do
  scp -o BatchMode=yes -o StrictHostKeyChecking=no $TINYDNS_ROOT/data.cdb root@$_host:$TINYDNS_ROOT/
  ssh -o BatchMode=yes -o StrictHostKeyChecking=no root@$_host svc -a /var/service/dnscache
done

svc -a /var/service/dnscache
