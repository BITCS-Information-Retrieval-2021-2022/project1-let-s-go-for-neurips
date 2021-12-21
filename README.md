# Let's Go For NeurIPS

- [Let's Go For NeurIPS](#head1)
    - [ 项目介绍](#head2)
    - [ 小组分工](#head3)
    - [ 功能特色](#head4)
        - [ 1、爬取数据自动去重](#head5)
        - [ 2、IP池爬取](#head6)
        - [ 3、线程池爬取](#head7)
        - [ 4、增量爬取](#head8)
        - [ 5、断点续爬](#head9)
        - [ 6、日志技术](#head10)
    - [ 整体效果](#head11)
    - [ 执行方法](#head12)
        - [ 1、运行环境](#head13)
        - [ 2、安装依赖](#head14)
        - [ 3、运行](#head15)
    - [ 第三方库依赖](#head16)
    - [ 系统架构](#head17)
        - [ 1、总体架构](#head18)
        - [ 2、爬虫服务](#head19)
    - [ 各模块执行原理](#head20)
        - [ 1、ACM](#head21)
        - [ 2、Springer](#head22)
        - [ 3、ScienceDirect](#head23)
        - [ 4、IP池服务](#head24)
        - [ 5、数据库](#head25)
    - [ 代码及文件结构](#head26)
# <span id="head1"> Let's Go For NeurIPS</span>

## <span id="head2"> 项目介绍</span>

我们的工作基于[scrapy](https://scrapy.org)框架实现了一个对学术网站的爬虫引擎，包括对[ACM](https://dl.acm.org)、[Springer](https://www.springer.com)、[ScienceDirect](https://www.sciencedirect.com)三个网站的论文爬取，爬取到的信息包括论文的各项信息、pdf文件以及视频url地址等，爬取到的数据存储在[MongoDB](https://www.mongodb.com)中，并通过[Elasticsearch](https://www.elastic.co)+[Kibana](https://www.elastic.co)搭建了一个检索系统，对爬取的数据建立索引进行展示。

## <span id="head3"> 小组分工</span>

| 姓名                                    | 学号       | 分工                           |
| --------------------------------------- | ---------- | ------------------------------ |
| 王昊    | 3120201035 |          |
| 刘文鼎  | 3120201080 |          |
| 何鹏    | 3120201036 |          |
| 王星煜  |3120201055  |          |
| 徐天祥  |3220200891  |          |
| 杨雪    | 3120201001 |          |


## <span id="head4"> 功能特色</span>

#### <span id="head5"> 1、爬取数据自动去重</span>

- 当爬虫爬取到相同论文时，在存入数据库时会自动去除重复数据

#### <span id="head6"> 2、IP池爬取</span>

- 部署了一个代理IP池，爬虫爬取时从IP池中获得一个随机可用的IP，增加爬虫的健壮性

#### <span id="head7"> 3、线程池爬取</span>

- 支持多线程爬取数据

#### <span id="head8"> 4、增量爬取</span>

- 支持增量式爬取，定时更新

#### <span id="head9"> 5、断点续爬</span>

- 出现网络崩溃或者手动终止时，可以从断点续爬

#### <span id="head10"> 6、日志技术</span>

- 爬虫的爬取信息和爬取状态会实时通过日志输出

## <span id="head11"> 整体效果</span>

- 数据库中共有记录***条

- 下载PDF共***篇

- 下载视频共***个

  **具体统计**（注：由于增量式爬取，有些论文被多个网站爬取，各网站爬取之和多于数据库记录）

  | 网站名        | 爬取数量 | 下载PDF数量 | 
  | ------------- | -------- | ----------- | 
  | ACM           |      |          |  
  | Springer      |     |        |  
  | ScienceDirect |    |        |   

  | 字段名          | 数量   | 覆盖率 | 备注                                                         |
  | ------------   | ------ | ------ | ------------------------------------------------------------ |
  | title          |  |   |                                                              |
  | abstract       |   |    |                                                              |
  | authors        |  |    |                                                              |
  | doi            |  |   |                                                              |
  | url            |  |   |  |
  | year           |   |   |                                          |
  | month          |  |   |                                                              |
  | type           |  |   |                                                              |
  | venue          |  |   |                                                              |
  | source         |  |  |                                                              |
  | video_url      |   |    |                                         |
  | video_path     |    |    |                                                              |
  | thumbnail_url  |   |  |                                                              |
  | pdf_url        |  |  |                                                              |
  | pdf_path       |   |   |                                         |
  | inCitations    |    |     |                                                              |
  | outCitations   |   |  |        

## <span id="head12"> 执行方法</span>

### <span id="head13"> 1、运行环境</span>

系统：Windows、Linux、MacOS

软件：python3

### <span id="head14"> 2、安装依赖</span>

```
pip install -r requirements.txt
```

### <span id="head15"> 3、运行</span>

- 将仓库克隆至本地

- 修改`config.yaml`和`start_urls.txt`(如果需要)

- 执行`scrapy crawl ***`，例如爬取ACM网站则执行`scrapy crawl ACM`

## <span id="head16"> 第三方库依赖</span>
参见`./requirements.txt`
## <span id="head17"> 系统架构</span>

### <span id="head18"> 总体架构</span>

![总体架构](./extra/structure.png)

系统整体基于Scrapy爬虫框架，对Middelware层和Pipeline层进行了重写，分别完成爬取时的身份代理与下载器的配置，在此基础上针对不同网站的爬取规则实现了三种不同的Spiders。系统外围还集成了代理IP池采集模块，数据存储模块与数据可视化模块

### <span id="head19"> 爬取流程</span>

![爬取流程](./extra/scrapy.png)

系统首先输入的爬取网站，读取预定义的爬取约束信息，然后通过中间件从预先爬取的代理IP池中随机选取一个可用IP，使用代理IP下载网站页面，并对页面内容进行解析，根据解析结果提取论文相关信息，并启动下载器对PDF、视频等文件进行下载，将数据分别存储到MongoDB
与本地磁盘，然后根据预定义的遍历规则与约束条件，对其他页面进行爬取，直到所有任务完成。

## <span id="head20"> 各模块执行原理</span>

### <span id="head21"> 1、ACM</span>

### <span id="head22"> 2、Springer</span>

### <span id="head23"> 3、ScienceDirect</span>

### <span id="head24"> 4、IP池服务</span>
对于ACM、Springer、ScienceDirect网站的反爬限制，采用代理IP的方式，定期爬取和更新代理IP池，在爬取论文是随机更换代理IP。

代理IP池需定期更新，对代理网站的免费代理进行持续采集，保存到proxylist.txt代理IP池本地文件。

**代理源**

- [快代理](www.kuaidaili.com)

### <span id="head25"> 5、数据库</span>
MongoDB是一个基于分布式文件系统的开源数据库系统，数据存储为一个文档，数据结构由键值对组成。文档类似于json对象，字段值可以包含其他文档，数据及文档数组。  
#### 5.1、执行流程
对爬取到的每一篇论文根据论文标题计算一个`checksum`值，根据`checksum`判断论文是否已经在数据库中了，如果已在数据库中则对已有数据进行更新，否则执行插入操作。
#### 5.2、checksum计算规则
使用正则表达式：
```python
checksum = re.sub(r'[\W\d\_]', "", info['title']).lower()
```
`checksum`即去除论文标题中除了字母和数字以外的所有字符，并将字母全部取小写。
#### 5.3、接口定义
采用`python`中的第三方库`pymongo`与数据库进行交互。  
具体代码参见`./Reptiles/Reptiles/mongodb.py`。  
- 连接数据库：
```python
Mongo = MongoManager()
```
- 插入及更新数据：
```python
Mongo.mongodb_insert(site, info)
```
- 删除数据：
```python
Mongo.mongodb_delete(site, field, value)
```
- 查询数据：
```python
Mongo.mongodb_find(site, field, value)
```

## <span id="head26"> 代码及文件结构</span>
- 代码结构
```
.
│  README.md
│  requirements.txt
│
└─Reptiles
    │  scrapy.cfg
    │  start.bat
    │
    └─Reptiles
        │  convert_json.py
        │  items.py
        │  middlewares.py
        │  mongodb.py
        │  pipelines.py
        │  proxy.py
        │  settings.py
        │  __init__.py
        │
        ├─configs
        │      proxylist_big.txt
        │
        └─spiders
                ACM.py
                ScienceDirect.py
                Springer.py
                __init__.py
```
- 文件结构
```

```
