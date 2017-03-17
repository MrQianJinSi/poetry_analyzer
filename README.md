# 全唐诗分析程序
这个程序最初的诞生是为了写微信公众号的两篇文章，那两篇文章的也大致讲解了程序的原理和流程。
因此，在使用程序之前，强烈建议您先读这两篇文章：
- [当我们在读唐诗时，我们在读什么？](https://mp.weixin.qq.com/s?__biz=MzI0NTUxMjgyOA==&mid=2247483724&idx=1&sn=9fe912aaaa2757eec2634a95931e1c6a&chksm=e94c2e5fde3ba749e4e364644d6b68d004b295a6864606c79f710b4b0e7e5d07ac3e89481012&mpshare=1&scene=1&srcid=0314cTnPXrmiKE1tR18sIV5m&pass_ticket=LmF1XSUkX6AZUuMnsPEO3vBZgEqfwt9frF%2F%2FATtYfAWYcIhzbawA0%2FclwgYNC1u%2F#rd)
- [计算机告诉你，唐朝诗人之间的关系到底是什么样的？](https://mp.weixin.qq.com/s?__biz=MzI0NTUxMjgyOA==&mid=2247483750&idx=1&sn=dd883b547a3fc4343a3dcce1abea3719&chksm=e94c2e75de3ba7631ffd7abff8a89ea56fda63b2f3d3bb81fd845ef5fd3e9207b41230900288&mpshare=1&scene=1&srcid=0314HdoeYueFNse6H7j18qfx&pass_ticket=P5NYT1vI3xq6gboRVFuq64N9z2Yp0ADF4pMH3nRnXAhGuoM7eROG8O2lhVg%2BIvoR#rd)

相应的，程序也主要有两个方面的功能：
- 分析词频和词向量，对应第一篇文章
- 构建诗人之间的引用关系，对应第二篇文章

master分枝仅支持python3。python2分枝(感谢网友[carryme9527](https://github.com/carryme9527/poetry_analyzer)的工作，这个分枝主要是他的功劳)则支持python2。
程序主要有两个目录：
- data目录，用于存储全唐诗和CBDB数据库
- html目录，存储最终的社交网络关系网页

程序在运算过程中会dump一些中间运算结果，并存储在save目录(如果不存在会自动创建)中。

由于CBDB数据库很大，有400+M。github不允许上传这么大的文件，请大家自行去[CBDB官网](http://projects.iq.harvard.edu/chinesecbdb/%E4%B8%8B%E8%BC%89cbdb%E5%96%AE%E6%A9%9F%E7%89%88)下载单机版数据库，并且以cbdb_sqlite.db为文件名存储在data目录下。
# 依赖库
程序依赖了两个python库
``` shell
pip3 install thulac
pip3 install gensim
```
其中thulac用于分词，gensim用于word2vec.
这两个库只用于第一篇文章的分析。如果您只关心如何构建诗人关系网络，那么不需要安装这个两个库。

# 基本用法
对于**普通用户**来说：
直接用浏览器打开html目录下的网页文件，就可以在浏览器中观察网络结构了，并且可以随意拖动和放大，很有意思。

对于**程序员**来说：
- 运行`python3 word_level_analyzer.py`来复现第一篇文章的结果
- 运行`python3 construct_poets_network.py`来构建社交网络，并将运行结果存储在save目录。
- 运行`python3 visualize_poets_network.py`来构建出显示社交网络的网页，并将结果存储在html目录。
# 路线图
我后续还会对古典文献进行一些分析，并将更新过的代码及时的push到这个库中。欢迎大家关注我的微信公众号：mrqianjinsi
