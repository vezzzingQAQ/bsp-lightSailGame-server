## 驭光而行-交互程序-服务器

### 运行环境

win11 python3.11.1

### 环境搭建

```cmd
python -m venv .venv

cd .venv/Scripts
./Activate.ps1

cd ..
cd ..
pip install -r requirements.txt
```

### 项目运行

```cmd
cd Server

python server.py
```

会同时弹出CMD和GUI窗口

### 接口

/getStars/{posx}/{posy}/{posz}/{dist} 

获取指定范围内天体数据
如果范围内没有，会寻找最近的一颗天体并返回
附带随机生成的行星数据

_powered by vezzzingQAQ_