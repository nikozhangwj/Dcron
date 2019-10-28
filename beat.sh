#!/usr/bin/env bash
# beat runing script

celerybin=/data/jms/venv/bin/celery
celery_pid_file=/opt/DCron/tmp/celery.pid
celery_log_file=/opt/DCron/logs/celery/celery.log

beat_pid_file=/opt/DCron/tmp/beat.pid
scheduler="django_celery_beat.schedulers:DatabaseScheduler"


celery_start(){
   # $celerybin  multi start  -A Dcron worker --pidfile=$celery_pid_file --logfile='$celery_log_file' -l info --autoscale 20,4
   # $celerybin worker -A Dcron -l INFO --pidfile $celery_pid_file --logfile $celery_log_file --autoscale 20,4
   ${celerybin} beat -A Dcron -l INFO --pidfile ${beat_pid_file} --scheduler ${scheduler} --max-interval 60
}


celery_stop(){
   $celerybin  multi stopwait  -A Dcron worker --pidfile=$celery_pid_file --logfile='$celery_log_file' -l info
}



test_status(){
    if test -e $celery_pid_file
    then
        echo 'celery is runing'
    else
        echo 'celery stoped'
    fi

}

case $1 in
start)
    celery_start
    ;;
stop)
    celery_stop
    ;;
status)
    test_status
    ;;
  *)
    echo './celery.sh start | stop | status'
    ;;
esac
