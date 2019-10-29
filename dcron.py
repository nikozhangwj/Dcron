#!/usr/bin/env python3
# encoding: utf-8

import os
import sys
import time
import argparse
import signal
import subprocess
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


os.environ["PYTHONIOENCODING"] = "UTF-8"
LOG_DIR = os.path.join(BASE_DIR, 'logs')
TMP_DIR = os.path.join(BASE_DIR, 'tmp')
all_services = ['gunicorn', 'celery', 'beat']
START_TIMEOUT = 60
WORKERS = 4
DAEMON = False
DEBUG = True
HTTP_HOST = '10.128.1.197'
HTTP_PORT = 8000


def get_log_file_path(service):
    return os.path.join(LOG_DIR, '{}.log'.format(service))


def get_pid_file_path(service):
    return os.path.join(TMP_DIR, '{}.pid'.format(service))


def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def get_pid(service):
    pid_file = get_pid_file_path(service)
    if os.path.isfile(pid_file):
        with open(pid_file) as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return 0
    return 0


def is_running(s, unlink=True):
    pid_file = get_pid_file_path(s)

    if os.path.isfile(pid_file):
        pid = get_pid(s)
        if check_pid(pid):
            return True

        if unlink:
            os.unlink(pid_file)
    return False


def parse_service(s):
    if s == 'all':
        return all_services
    elif "," in s:
        return [i.strip() for i in s.split(',')]
    else:
        return [s]


def start_gunicorn():
    print("\n- Start Gunicorn WSGI HTTP Server")
    service = 'gunicorn'
    bind = '{}:{}'.format(HTTP_HOST, HTTP_PORT)
    log_format = '%(h)s %(t)s "%(r)s" %(s)s %(b)s '
    pid_file = get_pid_file_path(service)
    log_file = get_log_file_path(service)

    cmd = [
        '/data/jms/venv/bin/gunicorn', 'Dcron.wsgi',
        '-b', bind,
        #'-k', 'eventlet',
        '-k', 'gthread',
        '--threads', '10',
        '-w', str(WORKERS),
        '--max-requests', '4096',
        '--access-logformat', log_format,
        '--access-logfile', log_file,
        '-p', pid_file,
    ]

    if DAEMON:
        cmd.extend([
            '--daemon',
        ])
    else:
        cmd.extend([
            '--access-logfile', '-'
        ])
    if DEBUG:
        cmd.append('--reload')
    p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr, cwd=BASE_DIR)
    return p


def start_celery():
    print("\n- Start Celery as Distributed Task Queue")
    # Todo: Must set this environment, otherwise not no ansible result return
    os.environ.setdefault('PYTHONOPTIMIZE', '1')

    if os.getuid() == 0:
        os.environ.setdefault('C_FORCE_ROOT', '1')

    service = 'celery'
    pid_file = get_pid_file_path(service)

    cmd = [
        '/data/jms/venv/bin/celery', 'worker',
        '-A',  'Dcron',
        '-l', 'INFO',
        '--pidfile', pid_file,
        '--autoscale', '20,4',
        '--logfile', os.path.join(LOG_DIR, 'celery.log'),
    ]
    if DAEMON:
        cmd.extend([
            '--detach',
        ])
    p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr, cwd=BASE_DIR)
    return p


def start_beat():
    print("\n- Start Beat as Periodic Task Scheduler")

    pid_file = get_pid_file_path('beat')
    log_file = get_log_file_path('beat')

    os.environ.setdefault('PYTHONOPTIMIZE', '1')
    if os.getuid() == 0:
        os.environ.setdefault('C_FORCE_ROOT', '1')

    scheduler = "django_celery_beat.schedulers:DatabaseScheduler"
    cmd = [
        '/data/jms/venv/bin/celery',  'beat',
        '-A', 'Dcron',
        '--pidfile', pid_file,
        '-l', 'INFO',
        '--scheduler', scheduler,
        '--max-interval', '60',
        '--logfile', log_file,
    ]
    if DAEMON:
        cmd.extend([
            '--detach',
        ])
    p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr, cwd=BASE_DIR)
    return p


def start_flower():
    print("\n- Start Celery flower")
    cmd = [
        '/data/jms/venv/bin/celery',
        'flower',
        '-A' ,'Dcron',
        '--address=', '0.0.0.0',
        '--port=', '5555'
    ]
    p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr, cwd=BASE_DIR)
    return p


def start_service(s):
    print(time.ctime())

    services_handler = {
        "gunicorn": start_gunicorn,
        "celery": start_celery,
        "beat": start_beat,
        "flower": start_flower
    }

    services_set = parse_service(s)
    processes = []
    for i in services_set:
        if is_running(i):
            show_service_status(i)
            continue
        func = services_handler.get(i)
        p = func()
        processes.append(p)

    now = int(time.time())
    for i in services_set:
        while not is_running(i):
            if int(time.time()) - now < START_TIMEOUT:
                time.sleep(1)
                continue
            else:
                print("Error: {} start error".format(i))
                stop_multi_services(services_set)
                return

    stop_event = threading.Event()

    if not DAEMON:
        signal.signal(signal.SIGTERM, lambda x, y: stop_event.set())
        while not stop_event.is_set():
            try:
                time.sleep(10)
            except KeyboardInterrupt:
                stop_event.set()
                break

        print("Stop services")
        for p in processes:
            p.terminate()

        for i in services_set:
            stop_service(i)
    else:
        print()
        show_service_status(s)


def stop_service(s, sig=15):
    services_set = parse_service(s)
    for s in services_set:
        if not is_running(s):
            show_service_status(s)
            continue
        print("Stop service: {}".format(s))
        pid = get_pid(s)
        os.kill(pid, sig)


def stop_multi_services(services):
    for s in services:
        stop_service(s, sig=9)


def stop_service_force(s):
    stop_service(s, sig=9)


def show_service_status(s):
    services_set = parse_service(s)
    for ns in services_set:
        if is_running(ns):
            pid = get_pid(ns)
            print("{} is running: {}".format(ns, pid))
        else:
            print("{} is stopped".format(ns))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""
        Dcron service control tools;

        Example: \r\n

        %(prog)s start all -d;
        """
    )
    parser.add_argument(
        'action', type=str,
        choices=("start", "stop", "restart", "status"),
        help="Action to run"
    )
    parser.add_argument(
        "service", type=str, default="all", nargs="?",
        choices=("all", "gunicorn", "celery", "beat", "celery,beat"),
        help="The service to start",
    )
    parser.add_argument('-d', '--daemon', nargs="?", const=1)
    parser.add_argument('-w', '--worker', type=int, nargs="?", const=4)
    args = parser.parse_args()
    if args.daemon:
        DAEMON = True

    if args.worker:
        WORKERS = args.worker

    action = args.action
    srv = args.service

    if action == "start":
        start_service(srv)
    elif action == "stop":
        stop_service(srv)
    elif action == "restart":
        DAEMON = True
        stop_service(srv)
        time.sleep(5)
        start_service(srv)
    else:
        show_service_status(srv)