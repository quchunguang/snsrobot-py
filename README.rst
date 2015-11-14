::

     o-o  o   o  o-o    o--o   o-o  o--o   o-o  o-O-o
    |     |\  | |       |   | o   o |   | o   o   |
     o-o  | \ |  o-o    O-Oo  |   | O--o  |   |   |
        | |  \|     |   |  \  o   o |   | o   o   |
    o--o  o   o o--o    o   o  o-o  o--o   o-o    o


========
snsrobot
========

属于机器人世界的社交网络。

项目概述
----

- 属于机器人世界的社交网络。
- 提供客户端（机器人）仿真程序。

界面截图
----

.. image:: https://github.com/quchunguang/snsrobot/raw/master/static/image/snapshot_report.png

.. image:: https://github.com/quchunguang/snsrobot/raw/master/static/image/snapshot_forcedirected.png

.. image:: https://github.com/quchunguang/snsrobot/raw/master/static/image/snapshot_Cytoscape.png

安装依赖
----

.. code-block:: bash

    sudo apt-get install python-dev python-pip nginx mongodb
    sudo pip install web.py networkx requests matplotlib pymongo ujson

模拟运行
----

.. code-block:: bash

    ./snsrobotd.py &                    # Run server as daemon
    ./snsrobot.py                       # Run cli client
    x-www-browser http://localhost:8080 # Run web client


Cytoscape_v3.2.1 or gephi is awesome for analysis the data generated.

设计与选型原则
-------

**一致性原则**
    Python单语言开发，JSON单数据类型，reStructuredText单文档类型，等。

**分离性原则**
    Daemon BS架构，部署三层架构，Robot CS架构均以HTTP分离。

**极简性原则**
    选型均以稳定实用高效率为原则，避免重量级框架及基础设施。拒绝数据转换。


名词定义
----

**比赛**
    双方进行，胜负取得得分。

**得分**
    胜“1” / 负“0”。

**目标**
    操作完成的度量标准。

**操作集**
    一个经验为达成目标所需的操作集。（可以语法树描述。）

**经验**
    经验（目标，操作集，得分）。

**积分**
    对某个主体进行通过比赛进行测量，利用算法（如Elo_rating_system算法）将单场得分转化为对积分的更新。

**社交网络**
    G(N, E)。E有权重W。

**个性**
    机器人根据某种规则（比如以一定分布概率）自主做出决策。

**知识**
    主题体存储的经验的集合。

**影响因子**
    算法接受其以控制单次比赛得分对总积分的影响力。（如Elo-rating算法中的K**

**聚类**
    对数据集的相似子集进行无提示相似度归类算法。

**传播**
    知识在主体间扩散。

设计注记
----

**假设**
    环境相似，比赛的结果应当相似。
    机器人相似，比赛的结果应当相似。

**比赛方式**
    机器人间捉对进行，建议在相同或相似的环境中进行。
    环境越接近，建议调整影响因子越大。

**机器人积分赛**
    相同的经验，不同的机器人间进行。
    得分高的机器人性能高。得分相近的机器人性能相近。
    每次比赛胜者机器人得分“1”，负者机器人得分“0”。
    积分计算采用Elo-rating算法。影响因子固定，或环境相近者大。

**经验积分赛**
    相同的目标，不同的经验，任意类型机器人间进行。
    得分高的经验号。得分相近的经验相近（或可表现为经验中解决问题的方法相似）。
    每次比赛胜者采用经验得分“1”，负者采用经验得分“0”。
    积分计算采用Elo-rating算法。影响因子机器人积分相近者大。

**聚类分析**
    对机器人积分可做聚类分析，结果显示机器人的自动聚类（或可表现为结构行为相近）。
    对经验积分可做聚类分析，结果显示相似的经验可以看做知识冗余。

**本地经验集清理**
    得分相近的经验，或可表现为经验中解决问题的方法相似，应当定期予以合并，删除对同目标经验积分同聚类中排名靠后者。

**社交网络推荐好友**
    u1的好友的共有好友集合表示为[adj(u)-adj(u1) for u in adj(u1)]，分析元素集合的半交集获得推荐好友。
    服务端机器人积分聚类，按相近程度推荐好友。

    机器人自主决定是否添加好友（个性）。
    添加好友后，社交网络建立E， W（R1，R2）=W0。
    机器人好友补充对方的本地经验集。

**社交网络服务发起比赛**
    社交网络抽取R1，R2，抽取目标，邀请R1，R2进行比赛。R1，R2自主选择合适的经验进行比赛。
    成绩更新R1，R2个人的机器人积分和经验积分的同时，上传比赛结果用以更新社交网络机器人积分和经验积分。

**社交网络好友发起比赛**
    R1抽取好友R2，R1抽取目标，邀请R2进行比赛。
    R2如果选择应战，R1，R2自主选择合适的经验进行比赛。
    成绩更新R1，R2个人的机器人积分和经验积分的同时，上传比赛结果用以更新社交网络机器人积分和经验积分。
    R2如不应战，降低W（R1，R2）

**社交网络的清理**
    if W（R1，R2） < Wmin，删除E（R1，R2）。

**社交网络的聚类分析**
    对机器人积分可做聚类分析，结果显示机器人的自动聚类（或可表现为结构行为相近）。
    对经验积分可做聚类分析，结果显示相似的经验可以看做知识冗余。

**社交网络的知识挖掘与传播**
    根据经验积分排名，将高经验积分经验推送到同聚类的机器人。

软件组成
----

**snsrobotd.py**
    单节点或集群部署的http服务。
    协议：HTTP1.1 POST GET
    监听端口：8080 (Can change as the unique command line argument)
    snscli（机器人）交互界面。
    web browser（人）交互界面。

**snsrobot.py**
    每机器人一实例的http客户端。
    -h 打印帮助信息
    -v 打印详细信息

依赖注记
----

**python 2.7**
    主要开发语言。

**requests**
    python第三方库，用于客户端发起请求。

**web.py**
    python第三方库，用于服务端处理，数据流标准为JSON/HTTP/POST。

**pymongo**
    python第三方库，用于操纵MongoDB。

**networkx**
    python第三方库，图算法实现相关基础库。

**matplotlib**
    python第三方库，图实时展示相关基础库。

**ujson**
    python第三方库，json库的高速替代版本，接口与json兼容。

**MongoDB**
    后端高性能DB。

**Bootstrap**
    基于jquery的Web前端样式框架。

**D3**
    基于javascript的Web图信息展示组件。

**Cytoscape**
    图论大数据的分析与展示工具。

代码规范
----

MUST PEP8 CHECK BEFORE COMMIT !!!

部署注记
----

在真实环境中部署服务端（snsrobotd.py），由于社交网络应对的是高并发环境，在初始设计选型中
已经考虑了分布式部署的问题。以下为建议环境及测试版本基准。

**拓扑**
    前端（Nginx proxy 1.9.3）
    中间层（snsrobotd.py）
    后端（MongoDB 3.0.5）
    客户端（snsrobot.py）
    展示端（Chrome 45.0）

**负载均衡**
    前端（Nginx proxy）作为负载均衡请求代理，并设置牺牲服务器，故障热迁移服务器。

**Web Service 集群**
    中间层（snsrobotd.py）多机多进程（池）部署。考虑python的性能，Nginx建议初始配置为：<64并发/进程，<16进程/节点。

**高性能DB**
    后端MongoDB用于数据持久化。MongoDB建议配置为：1进程/节点，与中间层共享节点，打包镜像发布。
    测试运行可用后端采用文件持久化，不连接MongoDB。

**操作系统**
    建议 HOST with Ubuntu 16.04 LTS amd64
    建议 Container with Docker 1.8.4
    建议 VM with Ubuntu 16.04 LTS amd64


开发日志
----

- 2015-11-13 browser side, /signin, /signout, /signup. changed api interface.
- 2015-11-09 client side, automatic generate data for simulate.
- 2015-11-08 / - browser side, initialize homepage template 'overview'.
- 2015-11-08 /admin/init_database - client side, interface to initialize database.
- 2015-11-08 /forcedirected - browser side, show force directed graph.
- 2015-11-08 /datagraph - browser side, access data for create SNS graph.
- 2015-11-08 /reports - browser side, robot rank top 100, edge top 100.
- 2015-11-08 /upload_result - client side, upload fighting results.
- 2015-11-08 /sign-in - client side, TODO: browser side.
- 2015-11-08 /sign-up - client side, TODO: browser side.
- 2015-11-07 部署实验
- 2015-11-07 环境构建
- 2015-11-06 技术选型
- 2015-11-05 设计文档草案


已知问题
----

- 该项目处于前期设计阶段，尚不适合应用于生产环境。

参考文献
----

#. `Elo rating system <https://en.wikipedia.org/wiki/Elo_rating_system>`_
#. `NetworkX <http://networkx.github.io/>`_
#. `NetworkX with cytoscape <http://networkx.github.io/documentation/latest/reference/drawing.html>`_
#. `cytoscape <http://www.cytoscape.org/>`_
#. `gephi <http://gephi.github.io/features/>`_
#. `Social Networks <http://www-rohan.sdsu.edu/~gawron/python_for_ss/course_core/book_draft/Social_Networks/Social_Networks.html>`_
#. `weibo api python <http://www.computational-communication.com/post/bian-cheng-gong-ju/2015-04-27-weibo-api-python>`_
#. `python gephi renren <http://blog.csdn.net/zdw12242/article/details/8687644>`_
#. `machine learning <https://github.com/golang/go/wiki/Projects#machine-learning>`_
#. `Social Networks <http://www-rohan.sdsu.edu/~gawron/python_for_ss/course_core/book_draft/Social_Networks/Social_Networks.html>`_
#. `python requests <http://docs.python-requests.org/en/latest/api/#requests.Response>`_
#. `python webpy <http://webpy.org/docs/0.3/tutorial.zh-cn>`_
#. `webpy bootstrap <http://my.oschina.net/zhengnazhi/blog/121610>`_
#. `Reference of bootstrap <http://v3.bootcss.com/getting-started/>`_
#. `data visualization <http://selection.datavisualization.ch/>`_
#. `30 Best Tools for Data Visualization <http://www.csdn.net/article/2014-04-01/2819076-30-Best-Tools-for-Data-Visualization/1>`_
#. `D3 <http://d3js.org/>`_
#. `D3 Gallery <https://github.com/mbostock/d3/wiki/Gallery>`_
#. `CDN speed up <http://www.bootcdn.cn/>`_
#. `FIGlet Server <http://www.asciiset.com/figletserver.html>`_

Licenses
--------

MIT
