## python虚拟环境

```
sudo pip3 install virtualenv virtualenvwrapper
vi ~/.bash_profile
   export WORKON_HOME=$HOME/.virtualenvs
   export PROJECT_HOME=$HOME/workspace
   export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
   source /usr/local/bin/virtualenvwrapper.sh
```

创建虚拟环境：mkvirtualenv [虚拟环境名称]

列出虚拟环境：lsvirtualenv

切换虚拟环境：workon [虚拟环境名称]

deactivate: 退出终端环境


rmvirtualenv ENV：删除运行环境ENV

mkproject mic：创建mic项目和运行环境mic

mktmpenv：创建临时运行环境

lssitepackages: 列出当前环境安装了的包

lsvirtualenv: 列出可用的运行环境
