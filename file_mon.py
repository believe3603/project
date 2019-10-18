from os.path import join, getsize
import os
import time
import shutil
import glob
import datetime
import zipfile



class File_mon():


    def __init__(self):
        self.importSr = r'G:\import'
        self.importDe = r'G:\des'
        self.s3path = r's3://jiahe-bucket/test/'


    #获取文件夹大小
    def Mon_file_size(self):
        size = 0
        """
           压缩指定文件夹
           :param root: 所指的是当前正在遍历的这个文件夹的本身的地址
           :param dirs: 是一个 list，内容是该文件夹中所有的目录的名字(不包括子目录)
           :param files: 同样是 list, 内容是该文件夹中所有的文件(不包括子目录)
           :return: 
        """
        for root, dirs, files in os.walk(self.importSr):
            size += sum([getsize(join(root, name)) for name in files])
        size = round(size / 1024 / 1024, 0)
        return size


    #打印出文件的大小
    def print_size(self):
        file_size = self.Mon_file_size()
        print('文件上传完毕,文件总大小是：{:.0f}M'.format(file_size))


    #移动文件到指定文件夹
    def move_file(self):
        file = glob.glob(self.importSr + "\\*")
        for i in file:
            shutil.move(i, self.importDe)


    # 压缩文件
    def zipDir(self):
        """
            压缩指定文件夹
            :param outFullName: 压缩文件绝对路径+filename.zip
            :return: 无
        """
        print('开始文件压缩，请稍等...')
        outFullName = self.importDe + '\\' + 'new.zip'
        zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(self.importSr):
            relativePath = root.replace(self.importSr, '')
            for file in files:
                filepath = os.path.join(root, file)
                zip.write(filepath, os.path.join(relativePath, file))
        zip.close()
        print('文件压缩完毕')

    # 移动文件到s3
    def move_file_to_s3(self):

        print('文件上传至s3中，请稍等...')
        for file in os.listdir(self.importDe):
            file_to_s3_path = self.importDe + '\\' + file
            if os.system('aws s3 cp {0} {1}'.format(file_to_s3_path, self.s3path)) == 0:
                print('文件{0}上传至s3成功'.format(file))
            else:
                print('文件{0}上传至s3失败'.format(file))


    # 上传完文件，清空文件夹
    def del_dec_file(self):

        #清空self.importSr
        for file in os.listdir(self.importSr):
            shutil.rmtree(self.importSr + '\\' + file)
            print('文件夹{0}删除成功'.format(file))

        # 清空self.importDe
        for file in os.listdir(self.importDe):
            os.remove(self.importDe + '\\' + file)
            print('文件{0}删除成功'.format(file))


    # 获取命令执行时间
    def get_time_spend(self):
        file_size = self.Mon_file_size()
        start = time.perf_counter()
        self.move_file_to_s3()
        end = time.perf_counter()
        spend = end - start
        avg_speed = file_size / spend
        print('上传至s3所用时间：{:.0f}s, 平均{:.2f}m/s'.format(spend, avg_speed))


    #判断文件是否上传完毕
    def Mon_get_file_size(self):


        file_list = []
        flag = True
        while flag:

            #获取文件夹大小添加到列表
            file_size = self.Mon_file_size()
            file_list.append(file_size)
            time.sleep(2)
            if file_list[-1] != 0.0:

                if len(file_list) == 1:
                    continue

                elif len(file_list) > 1:
                    if file_list[-1] == file_list[-2]:
                        self.print_size()
                        file_list = []
                        try:
                            self.zipDir()
                        except PermissionError:
                            self.zipDir()
                        self.get_time_spend()
                        self.del_dec_file()
                        continue
                    else:
                        print('文件在上传中,请稍等...')
            else:
                now = str(datetime.datetime.now())
                print('{0} 没有要上传的文件...'.format(now))
                if len(file_list) > 20:
                    file_list = []
                continue


if __name__ == "__main__":

    get_file_size = File_mon()
    get_file_size.Mon_get_file_size()

