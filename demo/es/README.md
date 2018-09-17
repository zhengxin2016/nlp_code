# ElasticSearch安装配置

./bin/elasticsearch -d //locahost:9200

启动失败方法1：
``` 
sudo vi /etc/sysctl.conf
#添加 vm.max_map_count=655360
sudo sysctl -p
```

启动失败方法2：
```
sudo vi /etc/security/limits.conf
#添加 
# username hard nofile 655360
# username soft nofile 655360
```


./bin/kibana //localhost:5601

nohup ./bin/kibana > nohup.log 2>&1 &

pip install elasticsearch

## 内存设置
```
$ vi ./bin/elasticsearch
ES_JAVA_OPTS="-Xms2g -Xmx2g"
```

## ik分词器
[ik分词器github](https://github.com/medcl/elasticsearch-analysis-ik)

## 配置用户词表，停用词表
```
$vi elasticsearch-6.2.4/plugins/ik/config/IKAnalyzer.cfg.xml

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">
<properties>
	<comment>IK Analyzer 扩展配置</comment>
	<!--用户可以在这里配置自己的扩展字典 -->
	<entry key="ext_dict">custom/mydict.dic;custom/single_word_low_freq.dic</entry>
	 <!--用户可以在这里配置自己的扩展停止词字典-->
	<entry key="ext_stopwords">custom/ext_stopword.dic</entry>
 	<!--用户可以在这里配置远程扩展字典 -->
	<entry key="remote_ext_dict">location</entry>
 	<!--用户可以在这里配置远程扩展停止词字典-->
	<entry key="remote_ext_stopwords">http://xxx.com/xxx.dic</entry>
</properties>
```

## 配置同义词表
```
synonyms_path:elasticsearch-6.2.4/plugins/ik/config/
index_mappings:
{
  "settings": {
    "number_of_shards": 1, 
    "analysis": {
      "filter": {
        "my_synonym_filter":{
          "type":"synonym",
          "synonyms_path":"synonym.txt"
        }
      },
      "analyzer": {
        "ik_syno":{
          "type":"custom",
          "tokenizer":"ik_smart",
          "filter":["my_synonym_filter"]
        },
        "ik_syno_max":{
          "type":"custom",
          "tokenizer":"ik_max_word",
          "filter":["my_synonym_filter"]
        }
      }
    }
  },
  "mappings": {
    "doc":{
      "properties": {
        "item_name":{
          "type": "text",
          "analyzer": "ik_syno_max",
          "search_analyzer": "ik_syno_max"
        }
      }
    }
  }
}
```
---
## 字段类型
[字段类型](https://blog.csdn.net/chengyuqiang/article/details/79048800)
---
## _index
索引就是文档集合
## _type
类型是索引的一个分区

### match_all
```
GET /bank/_search
{
  "query": { "match_all": {} },
  "_source":["name", "age"],//返回字段设置
  "sort": [{ "age": "asc" }],
  "from":10,
  "size":10
}
```
### match
{"name":"hello world"}查询name字段包含“hello”或“world”的
```
GET /mytest/user/_search
{
  "query": {
    "match": {"name_text":"Tom cat"}
  },
  "_source": ["name_keyword", "age"],
  "size":3
}
```
### match_phrase
{"name":"hello world"}查询name字段包含“hello world”的
```
GET /mytest/user/_search
{
  "query": {
    "match_phrase": {"name_text":"cat"}
  }
}
```
### bool
将小的查询组成大的查询
bool must 且
bool should 或
bool must_not 非
```
GET /mytest/user/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "name_text": "tom" } },
        { "match": { "name_text": "cat" } }
      ]
    }
  }
}
```

### 给某个不创建索引
```
The index option controls whether field values are indexed. It accepts true or false and defaults to true. Fields that are not indexed are not queryable.
{
  "mappings": {
    "my_type": {
      "properties": {
        "status_code": {
          "type": "keyword",
          "index": "false",
        }
      }
    }
  }
}
```