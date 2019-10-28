import logging
import requests
from datetime import datetime, date
from celery import shared_task

from scheduled_tasks.utils import last_work_day

logger = logging.getLogger('scheduled_tasks')


@shared_task(name='test_func1')
def test_func1(*args, **kwargs):
    logger.debug(args)
    logger.debug(kwargs)
    logger.info(kwargs.get('keyword')) if kwargs.get('keyword') else logging.info("No keyword come in.")
    return True


@shared_task(name='test_func2')
def test_func2(*args, **kwargs):
    for arg in args:
        logger.info(arg)
    return True


@shared_task(name='test_func3')
def test_func3(*args, **kwargs):
    w = ""
    for i in args:
        w += i
    logger.info(w)
    return w


@shared_task(name='remind_zb')
def remind_zb(*args, **kwargs):
    HEADERS = {'Content-Type': 'application/json'}
    content = kwargs.get('content')
    web_hook = kwargs.get('web_hook')
    if not content:
        logger.error("No content error.")
        return False
    elif not web_hook:
        logger.error("No web_hook error.")
        return False
    else:
        try:
            content['markdown']['content'] = '<font color="warning">周报提醒</font>\n今天是{}\n请记得按时交周报'.format(datetime.now().strftime(u"%Y年%m月%d号"))
            logger.info(content)
            res = requests.post(url=web_hook, json=content, headers=HEADERS)
            logger.debug(res.text)
            return res.text
        except Exception as error:
            return error


@shared_task(name='remind_yb')
def remind_yb(*args, **kwargs):
    HEADERS = {'Content-Type': 'application/json'}
    content = kwargs.get('content')
    web_hook = kwargs.get('web_hook')

    # 如果今天不是最后一个工作日则返回False
    if date.today() != last_work_day():
        logger.info("月报发送日期不匹配")
        return False

    # 如果参数为空则返回False
    if not content:
        logger.error("No content error.")
        return False
    elif not web_hook:
        logger.error("No web_hook error.")
        return False
    else:
        try:
            content['markdown']['content'] = '<font color="warning">月报提醒</font>\n今天是{}\n请记得按时交月报'.format(datetime.now().strftime(u"%Y年%m月%d号"))
            logger.info(content)
            res = requests.post(url=web_hook, json=content, headers=HEADERS)
            return res.text
        except Exception as error:
            return error