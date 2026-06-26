# FlowMap - 高级流程图生成器插件

**作者:** sawyer-shi  
**邮箱:** sawyer36@foxmail.com  
**版本:** 0.0.4  
**类型:** Dify插件  
**仓库:** [GitHub](https://github.com/sawyer-shi/dify-plugins-flow_map)

### 版本信息

- **当前版本**: v0.0.4
- **发布日期**: 2026-06-21
- **兼容性**: Dify插件框架
- **Python版本**: 3.12+

#### 版本历史
- **v0.0.4** (2026-06-21):
  - 新增 `AI流程图` 工具，支持像 `AI脑图` 一样在工具参数中选择 Dify LLM 模型
  - 支持输入普通文本，由LLM自动总结生成Mermaid流程图结构
  - 支持选择输出流程图模式：上下结构、左右结构、自由结构
  - 支持可选下载AI生成的Mermaid源文件
- **v0.0.3** (2026-03-15): 更新了元素之间的防遮盖算法，确保元素之间不互相遮盖。
- **v0.0.2** (2025-10-18): 新增自由布局流程图功能，修复了之前版本存在的bug,提升了软件的稳定性和可靠性。
- **v0.0.1** (2025-09-12): 初始发布版本，包含智能分支检测、彩色箭头标签和高级布局优化功能

## 描述

一个强大的流程图生成插件，能够将Mermaid语法转换为美观、智能的PNG流程图，也支持通过用户选择的LLM模型，把普通文本自动总结成Mermaid流程图结构后再生成流程图。支持上下结构、左右结构、自由结构三种布局，适合中文流程梳理、业务流程说明、审批链路和产品需求整理。

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

- 🤖 **AI流程图功能**
  - 在工具参数中直接选择 Dify 已配置的 LLM 模型
  - 输入普通文本，自动总结为标准 Mermaid 流程图结构
  - 支持上下结构、左右结构、自由结构三种输出模式
  - 可选下载 AI 生成的 Mermaid 源文件，方便二次编辑
  
- 🎭 **丰富主题**
  - 现代渐变主题
  - 商务专业主题
  - 经典简约主题
  - 自定义主题支持
  
- 🔧 **本地处理**
  - **本地生成**: 流程图在本地生成，无需API Key，无需链接外部网络或服务
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

2. **AI自动生成流程图** ⭐
   - 在 Dify 中安装并配置好可用的 LLM 模型
   - 选择 `ai_flow_map` / `AI流程图` 工具
   - 在 `LLM模型` 中选择要使用的模型
   - 在 `文本内容` 中粘贴会议纪要、业务说明、审批规则、需求描述等普通文本
   - 在 `流程图模式` 中选择：
     - `上下结构`: 适合审批流程、操作步骤、主线清晰的业务流程
     - `左右结构`: 适合时间线、跨角色协作、管道式流程
     - `自由结构`: 适合分支较多或不确定布局的复杂流程
   - 运行后插件会先让 LLM 总结出 Mermaid 流程图，再在本地渲染成 PNG 流程图

3. **手动LLM集成**
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

### AI流程图（`ai_flow_map`）

把普通文本自动总结为 Mermaid 流程图，并生成 PNG 流程图。

- **必填**: `model_config`、`text_content`
- **可选**: `layout_mode`、`theme`、`filename`、`download_mermaid`
- **适用场景**: 会议纪要转流程图、业务流程梳理、审批链路说明、产品需求整理、操作步骤可视化
- **注意**: 使用该工具时，文本会发送给用户选择的 Dify LLM 模型进行总结

| 参数 | 必填 | Form | 示例 | 说明 |
| --- | --- | --- | --- | --- |
| `model_config` | 是 | form | Dify中选择的LLM | 用于总结文本并生成Mermaid流程图结构 |
| `text_content` | 是 | llm | `请把以下审批规则整理成流程图...` | 普通文本输入 |
| `layout_mode` | 否 | form | `free` | 输出布局，支持 `top_bottom`、`left_right`、`free` |
| `theme` | 否 | form | `modern` | 视觉主题，支持 `modern`、`classic`、`business`、`tech`、`minimal` |
| `filename` | 否 | llm | `order_approval` | 下载 Mermaid 源文件时使用的基础文件名 |
| `download_mermaid` | 否 | form | `true` | 是否同时输出 AI 生成的 Mermaid 源文件 |

使用示例：

```text
model_config: 选择一个可用的 Dify LLM 模型
text_content: 用户提交订单后，系统先检查库存；如果库存充足则创建订单并通知支付；如果库存不足则提示用户更换商品。
layout_mode: free
theme: modern
filename: order_flow
download_mermaid: true
```

输出结果：

- PNG流程图图片
- 如果 `download_mermaid=true`，同时输出AI生成的 Mermaid 源文件
- JSON摘要信息，包含布局模式、主题和生成的 Mermaid 内容

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
- **复杂流程**: 自动扩大节点间距，并优先使用贝塞尔曲线分流，必要时回退正交连线通道，减少自由结构中线条互相干扰

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
│   ├── ai_flow_map.py      # AI文本转流程图工具
│   ├── mermaid_lr.py      # 左右布局工具
│   ├── mermaid_tb.py      # 上下布局工具
│   ├── mermaid_free.py    # 自由布局工具
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
- **复杂路由**: 复杂自由结构流程图会使用贝塞尔曲线分流、连线通道偏移、正交折线回退、画布边界约束和标签避让

### 性能优化

- **Matplotlib后端**: 高质量矢量图形
- **内存高效**: 本地处理无外部API
- **快速渲染**: 为复杂流程图优化

## 安全与隐私说明

- 普通 Mermaid 流程图工具只在本地渲染图片，不需要调用外部模型。
- `AI流程图` 会把 `text_content` 发送给用户在 Dify 中选择的 LLM 模型，用于生成 Mermaid 流程图结构。
- 插件不会主动保存用户输入内容；生成流程图图片和 Mermaid 源文件仅用于本次工具输出。
- 如文本包含合同、隐私信息、商业机密，请确认所选 LLM 模型和 Dify 部署环境符合你的数据安全要求。

## 开发者信息

- **作者**: [@sawyer-shi](https://github.com/sawyer-shi)
- **邮箱**: sawyer36@foxmail.com 【正在寻找新的工作机会】
- **许可证**: MIT License
- **源码地址**: https://github.com/sawyer-shi/dify-plugins-flow_map
- **支持**: 通过Dify平台、GitHub Issues 和邮箱联系

## 许可证声明

本项目采用 MIT License 许可证。

---

**准备好创建精美的流程图了吗？**