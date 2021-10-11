# coding=utf-8
import requests
import re
import os
import threading

# 扫描指定目录，下载全部封面与图片
home_url = '' # 神秘网站地址
root = '' #需要扫描的存在神秘代码目录 如 ssis-xxx

src = './src/'
time_out = 10  # 连接超时时间 超时则跳过该贴

# 在同级目录新建文件夹存图片
if not os.path.exists(src):
    os.mkdir(src)

# 为请求增加一下头，获取图片
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
headers = {
    'User-Agent': user_agent
}


def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


# 获取url中的文本内容
def getUrlText(url):
    try:
        resp = requests.get(url, timeout=time_out)
        if resp.status_code == 200:
            return resp.text
    except requests.RequestException:
        print('请求异常')
        return None


def list_all_files(rootdir):
    _files = []

    # 列出文件夹下所有的目录与文件
    list_file = os.listdir(rootdir)

    for i in range(0, len(list_file)):

        # 构造路径
        path = os.path.join(rootdir, list_file[i])

        # 判断路径是否是一个文件目录或者文件

        if os.path.isdir(path):
            _files.append(path)

    return _files


# 根据url下载文件
def save_file(url, file_name, path=''):
    if path == '':
        path = src
    # 存在同名文件 不下载
    if os.path.exists(path + file_name):
        return None
    try:
        pic = requests.get(url, headers=headers, timeout=time_out)
        with open(path + file_name, 'wb') as f:
            f.write(pic.content)
            f.flush()
            print(file_name + '下载完成！')
    except Exception as e:
        print(Exception, ':', e)


def main(index, real_path):
    print(real_path)
    try:
        print("开始执行下载： " + str(index))
        index_url = home_url + index  # 拼接神秘代码获取地址
        print(index_url + "\n")
        res = getUrlText(index_url)  # 获取对应页面
        title = re.search('<h3>(.*?)</h3>', res, re.S).group(1).upper()  # search匹配正则 获取标题
        # title=re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\u3040-\u31FF])","",title)
        print(title)
        touch(real_path + title + '.torrent')
        pic1 = re.search('<a class="bigImage" href="(.*?)">', res, re.S).group(1)  # search获取封面大图需要拼接url
        pic1 = home_url + pic1
        print(pic1)
        save_file(pic1, title + '.jpg', real_path)

        pics = re.findall('<a class="sample-box" href="(.*?)">', res)  # findall获取全部预览
        print(pics)
        thread_list = []
        for i, j in enumerate(pics):
            # save_file(j, title + '-' + str(i) + '.jpg', real_path)
            t = threading.Thread(target=save_file, args=(j, title + '-' + str(i + 1) + '.jpg', real_path))
            thread_list.append(t)

        for t in thread_list:
            t.setDaemon(True)
            t.start()

        for t in thread_list:
            t.join()
        print("执行完毕 end")

    except Exception as e:
        print(Exception, ':', e)  # 部分可能会出错，捕获跳过


if __name__ == '__main__':

    dirs = list_all_files(root)
    for i in dirs:
        # 移除尾缀
        fanhao = i.replace(root, '').replace("-C", '').replace('-uncensored', '').replace("-c", '')
        print(fanhao)
        main(fanhao, i + '/')
