# Flow Map Plugin for Dify
## 流程图插件

**Author:** sawyer-shi  
**Version:** 0.0.1  
**Type:** plugin  

### Description | 描述

Convert Markdown or Mermaid to flowcharts locally, supporting left-right and top-bottom layout directions.

在本地将Markdown或Mermaid转换为流程图，支持左右流向和上下流向布局。

### Features | 功能特性

- 🎨 **Multiple Layout Support** | **多种布局支持**
  - Left-to-right layout | 左右布局
  - Top-to-bottom layout | 上下布局
  
- 📝 **Text Format Support** | **文本格式支持**
  - Markdown syntax | Markdown语法
  - Mermaid diagram syntax | Mermaid图表语法
  
- 🔧 **Local Generation** | **本地生成**
  - No external dependencies | 无外部依赖
  - Fast processing | 快速处理
  - Privacy-focused | 注重隐私

### Installation | 安装

1. **Clone the repository | 克隆仓库**
   ```bash
   git clone https://github.com/sawyer-shi/dify-plugins-flow_map.git
   cd flow_map
   ```

2. **Activate virtual environment | 激活虚拟环境**
   ```bash
   # Windows PowerShell
   .\flowmapvenv\Scripts\Activate.ps1
   
   # Windows Command Prompt
   .\flowmapvenv\Scripts\activate.bat
   
   # Linux/Mac
   source flowmapvenv/bin/activate
   ```

3. **Install dependencies | 安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

### Usage | 使用方法

#### Basic Usage | 基本用法

```python
from tools.flow_map import FlowMapGenerator

# Create flow map generator | 创建流程图生成器
generator = FlowMapGenerator()

# Generate from Markdown | 从Markdown生成
markdown_text = """
# Process Flow
1. Start
2. Process Data
3. Make Decision
4. End
"""

flowchart = generator.from_markdown(markdown_text, layout="left-right")
```

#### Mermaid Syntax | Mermaid语法

```python
# Generate from Mermaid | 从Mermaid生成
mermaid_text = """
graph TD
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Fix it]
    D --> B
    C --> E[End]
"""

flowchart = generator.from_mermaid(mermaid_text, layout="top-bottom")
```

### API Reference | API参考

#### FlowMapGenerator Class

##### Methods | 方法

- `from_markdown(text: str, layout: str = "left-right") -> dict`
  - Generate flowchart from Markdown text | 从Markdown文本生成流程图
  - **Parameters | 参数:**
    - `text`: Markdown formatted text | Markdown格式文本
    - `layout`: Layout direction ("left-right" or "top-bottom") | 布局方向
  - **Returns | 返回值:** Flowchart data dictionary | 流程图数据字典

- `from_mermaid(text: str, layout: str = "top-bottom") -> dict`
  - Generate flowchart from Mermaid syntax | 从Mermaid语法生成流程图
  - **Parameters | 参数:**
    - `text`: Mermaid formatted text | Mermaid格式文本
    - `layout`: Layout direction | 布局方向
  - **Returns | 返回值:** Flowchart data dictionary | 流程图数据字典

### Configuration | 配置

Environment variables can be configured in `.env` file:

环境变量可在`.env`文件中配置：

```env
# Plugin Settings | 插件设置
PLUGIN_NAME=flow_map
PLUGIN_VERSION=0.0.1
DEBUG=false

# Flow Map Settings | 流程图设置
MAX_NODES=100
MAX_CONNECTIONS=200
DEFAULT_LAYOUT=hierarchical

# File Storage | 文件存储
UPLOAD_FOLDER=./uploads
MAX_FILE_SIZE=10485760
```

### Development | 开发

#### Project Structure | 项目结构

```
flow_map/
├── app/                    # Main application | 主应用
├── tools/                  # Tool implementations | 工具实现
├── test/                   # Test cases | 测试用例
├── provider/               # Provider configurations | 提供者配置
├── _assets/                # Static assets | 静态资源
├── manifest.yaml           # Plugin manifest | 插件清单
├── requirements.txt        # Dependencies | 依赖
├── main.py                # Entry point | 入口点
└── README.md              # Documentation | 文档
```

#### Running Tests | 运行测试

```bash
# Run all tests | 运行所有测试
pytest test/

# Run with coverage | 运行并显示覆盖率
pytest test/ --cov=app --cov=tools
```

#### Building Plugin | 构建插件

```bash
# From project root directory | 从项目根目录执行
.\dify-plugin-windows-amd64.exe plugin package .\flow_map

# This will create flow_map-0.0.1.difypkg | 这将创建flow_map-0.0.1.difypkg文件
```

### Contributing | 贡献

1. Fork the repository | Fork仓库
2. Create a feature branch | 创建功能分支
3. Make your changes | 进行更改
4. Add tests | 添加测试
5. Submit a pull request | 提交拉取请求

### License | 许可证

This project is licensed under the MIT License.

本项目采用MIT许可证。

### Support | 支持

If you encounter any issues or have questions, please:

如果遇到问题或有疑问，请：

1. Check the documentation | 查看文档
2. Search existing issues | 搜索现有问题
3. Create a new issue | 创建新问题

### Changelog | 更新日志

#### v0.0.1 (2025-09-10)
- Initial release | 初始版本
- Basic Markdown and Mermaid support | 基础Markdown和Mermaid支持
- Left-right and top-bottom layouts | 左右和上下布局
