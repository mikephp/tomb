see Wiki.

*util*

- class-dump-z 是 https://code.google.com/p/networkpx/wiki/class_dump_z 0.2a的linux_x86版本. Ubuntu下如果显示没有找到libstdc++.so.6的话, 可以使用`sudo apt-get install lib32stdc++6-5-dbg`来安装.
- ipautil-macosx 是 在明华老师机器上编译出来的，链接使用libarchive的动态库版本。如果运行时候发现找不到这个库的话，那么需要手动安装。在这里可以下载到[libarchive](http://www.libarchive.org/)
- apktool Android APK反编译工具.

*market-analysis*

requirements
- java>=1.7
- python>=2.6
- 7z, mongodb, redis

以2015-10-22 coolchuan提供的Android top5000数据分析，所提供的市场有下面这些
```
set([u'baidu', u'anzhuoshichang', u'xiaomi', u'anzhi', u'wandoujia', u'vivo', u'meizu', u'oppo', u'liantong', u'yiyonghui', u'yingyonghui', u'huawei', u'yingyongbao', u'360', u'lianxiang', u'yidong', u'jifeng'])
```
但是部分市场是没有下载地址的。考虑到市场活跃情况，我们会下载 'baidu', 'xiaomi', 'yingyongbao', '360', 'huawei' 市场下的apk来分析. 然后对结果取交集来减少数据波动
