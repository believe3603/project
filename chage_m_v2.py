import os
import glob
import datetime
import time


#windows系统
dirpath = r'\\192.168.1.241\mnt\module\handle'

#linux系统
# dirpath = r'/data/mnt/module/handle'


#获取文件夹列表
def getdirlist():

    #windows系统
    file = glob.glob(dirpath + '\\' + str(datetime.date.today()) + "\\*")

    #linux系统
    # file = glob.glob(dirpath + '//' + str(datetime.date.today()) + "//*")
    return file

#日志输出
def log(detail):

    time_log = str(datetime.datetime.now())
    print(time_log + '  ' + detail)


flag = True

while flag:


    #windows系统
    if os.path.exists(dirpath + '\\' + str(datetime.date.today())):

    #linux系统
    # if os.path.exists(dirpath + '//' + str(datetime.date.today())):

        #判断是否第一次创建任务，会同时生成文件夹
        if len(getdirlist()) == 1:

            # os.system('chmod -R 775 %s' % (dirpath + '//' + str(datetime.date.today())))
            log('新的一天文件,文件修改成功')
        file_list1 = getdirlist()
        time.sleep(2)

        if os.path.exists(dirpath + '\\' + str(datetime.date.today())):
            file_list1 = getdirlist()
            time.sleep(1)
            print('新的一天开始了,重新获取文件列表')
        file_list2 = getdirlist()
        if len(file_list1) != len(file_list2):
            # os.system('chmod -R 775 %s' % (dirpath + '//' + str(datetime.date.today())))
            log('文件修改成功')
        else:
            log('没有新建任务...')
            continue
    else:
        log('没有可执行的任务...')
        time.sleep(3)
        continue

#nohup python -u chage_m.py > nohup.out 2>&1 &   (日志输出到nohup.out)