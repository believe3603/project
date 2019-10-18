import os
import shutil
import glob


class copyFile():

    def __init__(self):

        self.handleSr = r'\\192.168.1.241\mnt\data\work\MODIS\MOD09A1\MOD09A1\2019'
        self.handleDe = r"G:\data\MOD09A1"

    def FindSourceList(self):

        areaFileList = []
        #条带号
        stripTup = ["h27v06", "h28v06", "h27v05"]

        #以条带号过滤出文件
        for i in stripTup:
            areaList = glob.glob(self.handleSr + '\\' + '\\*\\*{0}*'.format(i))
            areaFileList += areaList


        #复制文件到指定的文件夹
        for j in areaFileList:
            #没有文件则创建文件夹
            if not os.path.isdir(self.handleDe):
                os.makedirs(self.handleDe)
            shutil.copy(j, self.handleDe)


if __name__ == "__main__":
    modis09a1 = copyFile()
    modis09a1.FindSourceList()