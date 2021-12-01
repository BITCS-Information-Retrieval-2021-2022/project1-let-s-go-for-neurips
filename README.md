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
    - [ 第三方库依赖](#head12)
    - [ 系统架构](#head11)
        - [ 1、系统总体](#head12)
        - [ 2、爬虫服务](#head13)
    - [ 各模块执行原理](#head19)
        - [ 1、ACM](#head20)
        - [ 2、Springer](#head26)
        - [ 3、ScienceDirect](#head29)
        - [ 4、IP池服务](#head35)
        - [ 5、数据库](#head49)
    - [ 代码及文件结构](#head55)
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

## <span id="head1"> 第三方库依赖</span>

## <span id="head1"> 系统架构</span>

### <span id="head13"> 1、系统总体</span>

### <span id="head14"> 2、爬虫服务</span>

## <span id="head12"> 各模块执行原理</span>

### <span id="head13"> 1、ACM</span>

### <span id="head14"> 2、Springer</span>

### <span id="head14"> 3、ScienceDirect</span>

### <span id="head14"> 4、IP池服务</span>

### <span id="head14"> 5、数据库</span>

## <span id="head12"> 代码及文件结构</span>