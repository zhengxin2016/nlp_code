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

## ik分词器
[ik分词器github](https://github.com/medcl/elasticsearch-analysis-ik)

