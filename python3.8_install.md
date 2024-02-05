# python3.8安装步骤(centos7)

## 1. 安装依赖包
```
sudo yum install zlib zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make libffi-devel
```

## 2. 安装openssl
```
sudo wget http://www.openssl.org/source/openssl-1.1.1.tar.gz

tar -zxvf openssl-1.1.1.tar.gz

cd openssl-1.1.1

./config --prefix=/usr/local/openssl shared zlib

sudo mkdir /usr/local/openssl

sudo chmod -R 777 /usr/local/openssl

## 如果make过程中出现错误，先执行sudo make clean，再从之前的./config步骤开始重新执行
sudo make && make install

## 如果不行可直接通过vim修改文件/etc/profile
sudo echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/openssl/lib" >>  /etc/profile 

source /etc/profile
```

## 3. 安装python源码包
```
wget https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tgz

tar -zxvf Python-3.8.12.tgz

./configure --prefix=/usr/local/python3 --with-openssl=/usr/local/openssl

sudo mkdir /usr/local/python3

sudo chmod -R 777 /usr/local/python3

## 如果make过程中出现错误，先执行sudo make clean，再从之前的./configure步骤开始重新执行
sudo make && make install

ln -s /usr/local/python3/bin/python3.8 /usr/bin/python3

ln -s /usr/local/python3/bin/pip3.8 /usr/bin/pip3
```