# FlowMap - 高级流程图生成器插件

**作者:** sawyer-shi  
**邮箱:** sawyer36@foxmail.com  
**版本:** 0.0.2  
**类型:** Dify插件  
**仓库:** [GitHub](https://github.com/sawyer-shi/dify-plugins-flow_map)

### 版本信息

- **当前版本**: v0.0.2
- **发布日期**: 2025-10-18
- **兼容性**: Dify插件框架
- **Python版本**: 3.12+

#### 版本历史
- **v0.0.2** (2025-10-18): 新增自由布局流程图功能，修复了之前版本存在的bug,提升了软件的稳定性和可靠性。
- **v0.0.1** (2025-09-12): 初始发布版本，包含智能分支检测、彩色箭头标签和高级布局优化功能

## 描述

一个强大的流程图生成插件，将Markdown和Mermaid语法转换为美观、智能的流程图，具有高级布局优化和分支感知定位功能。

## ✨ 核心功能

- 🎨 **智能布局系统**
  - 智能分支检测和复杂流程图自由布局
  - 线性流程网格布局
  - 自动画布尺寸防止元素溢出
  
- 📐 **多种布局方向**
  - 左右布局
  - 上下布局
  - 分支感知定位
  
- 🌈 **彩色箭头标签**
  - 基于标签语义的智能颜色映射
  - 支持中英文标签
  - 可定制颜色主题
  
- 📝 **双格式支持**
  - 完整Mermaid语法支持，包含标签箭头
  - Markdown列表转换
  - 自动文本类型检测
  
- 🎭 **丰富主题**
  - 现代渐变主题
  - 商务专业主题
  - 经典简约主题
  - 自定义主题支持
  
- 🔧 **本地处理**
  - **本地生成**: 脑图在本地生成，无需API Key，无需链接外部网络或服务
  - **安全可靠**: 数据不外泄，完全离线处理，保护用户隐私
  - 无外部API依赖
  - matplotlib快速生成
  - 注重隐私设计
  - 高质量PNG输出

## 🚀 快速开始

1. **从Dify插件市场下载**
   - 进入Dify插件市场
   - 搜索并下载 `flow_map` 插件
   - 在您的工作区中启用FlowMap插件

2. **LLM集成** ⭐
   - 在Dify工作流中添加LLM节点
   - 使用最简单的提示词：**"将用户输入#context#总结为Mermaid流程图文本格式"**
   - 将LLM输出连接到FlowMap插件输入

### 基本使用示例
<img width="2214" height="730" alt="flow_map_cn_a_01" src="https://github.com/user-attachments/assets/1b971d99-99e9-4686-9998-bba9fd26c0fd" />
<img width="2169" height="678" alt="flow_map_cn_c_01" src="https://github.com/user-attachments/assets/be139d4c-e60a-48ab-9886-d48349451c2a" />

**上下布局**
<img width="4177" height="7365" alt="flow_map_cn_a_02" src="https://github.com/user-attachments/assets/d2f8d83e-2b89-4fc1-8ec9-7ef90911bae4" />
<img width="4847" height="4438" alt="flow_map_cn_c_03" src="https://github.com/user-attachments/assets/b960291a-5aa3-49b4-8220-4c863a924da0" />

**左右布局**
<img width="7412" height="4151" alt="flow_map_cn_a_03" src="https://github.com/user-attachments/assets/a8a93a4d-4126-4ccb-b6e7-22a2ca219062" />
<img width="8700" height="2561" alt="flow_map_cn_c_02" src="https://github.com/user-attachments/assets/176dff9f-d249-487a-a45d-6a67532800f5" />

## 📚 API参考

### Mermaid左右布局工具

**输入参数:**
- `text` (字符串，必需): Mermaid语法流程图文本
- `theme` (字符串，可选): 主题名称 (modern/business/classic)

**输出:**
- 成功: PNG图像 + 文本摘要
- 格式: "Successfully generated left-right layout flowchart. File size: X.XXM. Contains X nodes and X connections."

### Mermaid上下布局工具

**输入参数:**
- `text` (字符串，必需): Mermaid语法流程图文本
- `theme` (字符串，可选): 主题名称 (modern/business/classic)

**输出:**
- 成功: PNG图像 + 文本摘要
- 格式: "Successfully generated top-bottom layout flowchart. File size: X.XXM. Contains X nodes and X connections."

## 🛠️ 高级功能

### 智能分支检测

插件自动检测流程图中的分支场景并切换布局算法：

- **线性流程**: 使用网格布局实现最优对齐
- **分支流程**: 使用自由布局防止重叠

### 彩色箭头标签

支持带标签的箭头和智能颜色映射：

```mermaid
F -->|通过| G    # 正面结果使用绿色箭头
F -->|不通过| H  # 负面结果使用红色箭头
F -->|待定| I    # 待定状态使用橙色箭头
```

### 主题定制

可用主题及不同视觉风格：

- **现代**: 清洁的渐变设计
- **商务**: 专业企业风格
- **经典**: 传统简约外观

## 🔧 开发

### 项目结构

```
flow_map/
├── tools/                  # 核心工具实现
│   ├── mermaid_lr.py      # 左右布局工具
│   ├── mermaid_tb.py      # 上下布局工具
│   └── optimized_layout.py # 高级布局引擎
├── provider/              # 提供者配置
├── test/                  # 综合测试
├── manifest.yaml          # 插件清单
├── main.py               # 入口点
└── README.md             # 文档
```



## 🔍 技术细节

### 分支感知布局算法

- **分支检测**: 自动识别具有多个出向连接的决策节点
- **自由布局**: 基于连接层级的分层定位
- **画布适配**: 动态画布尺寸（最多2.5倍节点数）
- **碰撞避免**: 70%有效区域使用率的智能间距

### 性能优化

- **Matplotlib后端**: 高质量矢量图形
- **内存高效**: 本地处理无外部API
- **快速渲染**: 为复杂流程图优化

## 📄 许可证

本项目采用MIT许可证 - 详见LICENSE文件。

## 🤝 支持

如果遇到问题或有疑问：

1. 📖 查看文档
2. 🔍 在GitHub上搜索现有问题
3. 🆕 创建新问题并详细描述
4. 💬 加入社区讨论
5. 📧 邮箱: sawyer36@foxmail.com

## 🙏 致谢

- 感谢Matplotlib团队提供的优秀绘图库
- 感谢Mermaid.js社区的启发
- 感谢Dify平台提供的插件框架