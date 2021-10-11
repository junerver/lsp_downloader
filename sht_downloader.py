# coding=utf-8
import requests
import re
import os
import threading

home_url = ''  # 神秘网站网址
column = 103  # 版块 
normal = './img/'  # 保存在同级目录下的img文件夹下
importent = './importent/'
time_out = 10  # 连接超时时间 超时则跳过该贴

# 在同级目录新建文件夹存图片
if not os.path.exists(normal):
    os.mkdir(normal)
if not os.path.exists(importent):
    os.mkdir(importent)
# 为请求增加一下头，获取图片
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
headers = {
    'User-Agent': user_agent
}


# 获取url中的文本内容
def getUrlText(url):
    try:
        resp = requests.get(url, timeout=time_out)
        if resp.status_code == 200:
            return resp.text
    except requests.RequestException:
        print('请求异常')
        return None


# 根据url下载文件
def save_file(url, file_name):
    # 筛选你的兴趣爱好
    if 'xx' in file_name or 'xxx' in file_name :
        path = importent
    else:
        path = normal
    # 存在同名文件 不下载
    if os.path.exists(path + file_name):
        return None
    try:
        pic = requests.get(url, headers=headers, timeout=time_out)
        with open(path + file_name, 'wb') as f:
            f.write(pic.content)
            f.flush()
            # print(file_name + '下载完成！')
    except Exception as e:
        print(Exception, ':', e)


def main(index):
    print("开始执行下载：第 " + str(index) + ' 页')
    # index_url = home_url + "forum.php?mod=forumdisplay&fid=" + str(column) + "&page=" + str(index)
    index_url = home_url + "forum-" + str(column) + "-" + str(index) + ".html"
    # print(index_url + "\n")
    res = getUrlText(index_url)  # 首页
    all_tie = re.findall('</em> <a href="(thread.*?html)', str(res), re.S)  # 匹配正则获取首页30个帖子id列表
    thread_list = []
    for i in all_tie:
        url = home_url + i  # 拼接真实帖子的url
        # print(url)
        tie_text = getUrlText(url)  # 获取帖子正文
        try:
            # 匹配正则 获取 标题、图片*2、附件
            title = re.search('<span id="thread_subject">(.*?)</span>', tie_text, re.S).group(1).upper()  # 匹配正则 获取标题
            # print(title)
            pic1 = re.search('class="zoom" file="(.*?)" ', tie_text, re.S).group(1)  # 获取封面
            # print(pic1)

            pic2 = re.search('<img id="aimg_.*?" aid=".*?" src=".*?" zoomfile="(.*?)" file=', tie_text, re.S).group(
                1)  # 获取预览
            # print(pic2)

            attnm = re.search('<p class="attnm">.*<a href="(.*)" onmouseover=.*.torrent</a>', tie_text, re.S).group(
                1).replace("amp;", "")  # 获取种子
            # print(attnm + '\n')

            # 多线程加速
            t1 = threading.Thread(target=save_file, args=(pic1, title + '-1.jpg'))
            t2 = threading.Thread(target=save_file, args=(pic2, title + '-2.jpg'))
            t3 = threading.Thread(target=save_file, args=(attnm, title + '.torrent'))
            thread_list.append(t1)
            thread_list.append(t2)
            thread_list.append(t3)
            # t1.start()
            # t2.start()
            # t3.start()

            # save_file(pic1, title + '-1.jpg')  # 保存封面
            # save_file(pic2, title + '-2.jpg')  # 保存预览
            # save_file(home_url + attnm, title + '.torrent')  # 保存种子文件
        except Exception as e:
            print(Exception, ':', e)  # 部分欧美无码可能会出错，捕获跳过

    for t in thread_list:
        t.setDaemon(True)
        t.start()

    for t in thread_list:
        t.join()

    print("执行完毕 end")


if __name__ == '__main__':
    # 使用多线程下载可能会出现下载失败的情况，重复几次
    index = input('输入需要下载的页码：')
    for i in range(1, 3):
        main(int(index))

    print('运行完毕')
