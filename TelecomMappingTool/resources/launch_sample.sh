VENDOR=<<VENDORNAME>>

cd /home/asentinel/auto_edi/vans/${VENDOR}/

echo "*** `date +%Y-%m-%d-%H:%M:%S` - EDI Process is beginning. ***" >>/home/asentinel/logs/${VENDOR}.log

if [ ! -e "/home/asentinel/auto_edi/vans/${VENDOR}/ediall.tmp" ]
then
  echo "*** `date +%Y-%m-%d-%H:%M:%S` - breaking ***" >>/home/asentinel/auto_edi/vans/${VENDOR}/ediall.tmp
  echo "*** `date +%Y-%m-%d-%H:%M:%S` - breaking ***" >>/home/asentinel/logs/${VENDOR}.log

  ./break.sh >> /home/asentinel/logs/${VENDOR}.log

  cd /home/asentinel/auto_edi/vans/${VENDOR}/
  rm /home/asentinel/auto_edi/vans/${VENDOR}/ediall.tmp
fi

echo "*** `date +%Y-%m-%d-%H:%M:%S` - EDI Process is complete. ***" >>/home/asentinel/logs/${VENDOR}.log
