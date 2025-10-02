# N8N PicEdit 节点安装指南

## 前提条件

- Node.js 16+ 已安装
- N8N 已安装并可正常运行
- Python 3.6+ 已安装
- 必要的 Python 依赖包

## Python 依赖安装

首先确保安装了必要的 Python 依赖：

```bash
pip install Pillow
# 或者如果您使用 conda
conda install pillow
```

## 安装方法

### 方法一：本地 npm 安装（推荐）

1. **找到您的 N8N 安装目录**：
   ```bash
   # 查找 N8N 安装位置
   which n8n
   npm list -g n8n
   ```

2. **复制包文件**：
   ```bash
   # 将 tgz 文件复制到合适的位置
   cp n8n-nodes-picEdit-0.1.0.tgz ~/n8n-custom-nodes/
   ```

3. **安装包**：
   ```bash
   # 方式1：直接安装
   npm install -g ./n8n-nodes-picEdit-0.1.0.tgz
   
   # 方式2：在项目目录中安装
   cd /path/to/your/n8n/project
   npm install ./n8n-nodes-picEdit-0.1.0.tgz
   ```

### 方法二：Docker 环境安装

如果您使用 Docker 运行 N8N：

1. **创建自定义 Dockerfile**：
   ```dockerfile
   FROM n8nio/n8n:latest
   
   USER root
   
   # 安装 Python 和依赖
   RUN apk add --no-cache python3 py3-pip
   RUN pip3 install Pillow
   
   # 复制并安装自定义节点
   COPY n8n-nodes-picEdit-0.1.0.tgz /tmp/
   RUN npm install -g /tmp/n8n-nodes-picEdit-0.1.0.tgz
   
   USER node
   ```

2. **构建镜像**：
   ```bash
   docker build -t n8n-with-picedit .
   ```

3. **运行容器**：
   ```bash
   docker run -it --rm \
     --name n8n \
     -p 5678:5678 \
     -v ~/.n8n:/home/node/.n8n \
     n8n-with-picedit
   ```

### 方法三：通过 N8N 界面安装

1. **启动 N8N**：
   ```bash
   n8n start
   ```

2. **在浏览器中打开** `http://localhost:5678`

3. **安装社区节点**：
   - 点击右上角的用户头像
   - 选择 "Settings"
   - 点击左侧的 "Community Nodes"
   - 点击 "Install a community node"
   - 输入包名或上传 tgz 文件

## 验证安装

### 1. 检查节点是否可用

重启 N8N 后，在节点面板中搜索 "PicEdit"，应该能看到新的节点。

### 2. 测试基本功能

创建一个简单的工作流：

1. **添加 PicEdit 节点**
2. **选择 "Create Canvas" 操作**
3. **选择 "Blank" 类型**
4. **设置画布尺寸**：800x600
5. **设置背景色**：#ffffff
6. **执行节点**

### 3. 测试中文路径功能

1. **准备测试图片**：
   - 创建一个包含中文的目录：`测试目录`
   - 在其中放置一张图片：`测试图片.jpg`

2. **创建工作流**：
   - 添加 PicEdit 节点
   - 选择 "Create Canvas" → "From Image"
   - 输入中文路径：`/path/to/测试目录/测试图片.jpg`
   - 执行节点

如果能正常执行且返回 base64 图片数据，说明安装成功。

## 故障排除

### 问题1：找不到 Python 脚本

**错误信息**：`Could not find Python script file`

**解决方案**：
```bash
# 检查 Python 脚本是否存在
find /usr/local/lib/node_modules -name "wrapper.py" 2>/dev/null
find ~/.n8n -name "wrapper.py" 2>/dev/null

# 如果找不到，重新安装包
npm uninstall -g n8n-nodes-picEdit
npm install -g ./n8n-nodes-picEdit-0.1.0.tgz
```

### 问题2：Python 依赖缺失

**错误信息**：`ModuleNotFoundError: No module named 'PIL'`

**解决方案**：
```bash
# 安装 Pillow
pip install Pillow

# 或者使用 conda
conda install pillow

# 检查安装
python -c "from PIL import Image; print('PIL installed successfully')"
```

### 问题3：中文路径仍然报错

**解决方案**：
1. 确保使用的是修复后的版本
2. 检查文件路径是否真实存在
3. 验证文件权限
4. 运行测试脚本：
   ```bash
   cd /path/to/node_modules/n8n-nodes-picEdit/python
   python test_chinese_path.py
   ```

### 问题4：权限问题

**错误信息**：`Permission denied`

**解决方案**：
```bash
# 给予执行权限
chmod +x /path/to/python/wrapper.py

# 或者使用 sudo 安装
sudo npm install -g ./n8n-nodes-picEdit-0.1.0.tgz
```

## 卸载

如果需要卸载节点：

```bash
# 全局卸载
npm uninstall -g n8n-nodes-picEdit

# 本地卸载
npm uninstall n8n-nodes-picEdit
```

## 更新

当有新版本时：

```bash
# 先卸载旧版本
npm uninstall -g n8n-nodes-picEdit

# 安装新版本
npm install -g ./n8n-nodes-picEdit-新版本.tgz
```

## 支持

如果遇到问题：

1. 检查 N8N 日志：`~/.n8n/logs/`
2. 检查 Python 脚本输出
3. 运行测试脚本验证功能
4. 查看详细错误信息

## 注意事项

- 确保 Python 和 Node.js 版本兼容
- 在生产环境中使用前充分测试
- 定期备份 N8N 配置和工作流
- 关注节点更新和安全补丁