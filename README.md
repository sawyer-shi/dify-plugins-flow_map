# FlowMap - Advanced Flowchart Generator Plugin for Dify

**Author:** sawyer-shi  
**Email:** sawyer36@foxmail.com  
**Version:** 0.0.4  
**Type:** Dify Plugin  
**Repository:** [GitHub](https://github.com/sawyer-shi/dify-plugins-flow_map)

### Version Information

- **Current Version**: v0.0.4
- **Release Date**: 2026-06-17
- **Compatibility**: Dify Plugin Framework
- **Python Version**: 3.12+

#### Version History
- **v0.0.4** (2026-06-17): Added `AI Flowchart` tool with Dify LLM model selection, plain text to Mermaid generation, top-bottom/left-right/free layout selection, and optional Mermaid source download.
- **v0.0.3** (2026-03-15): Updated element overlap prevention algorithm to ensure elements do not cover each other.
- **v0.0.2** (2025-10-18): Added free layout flowchart functionality, fixed bugs from previous versions, improved software stability and reliability.
- **v0.0.1** (2025-09-12): Initial release with smart branch detection, colorful arrow labels, and advanced layout optimization

## Description

A powerful flowchart generation plugin that converts Mermaid syntax or AI-summarized plain text to beautiful, intelligent flowcharts with advanced layout optimization and branch-aware positioning.

## ✨ Key Features

- 🎨 **Intelligent Layout System**
  - Smart branch detection and free layout for complex flowcharts
  - Grid layout for linear processes
  - Automatic canvas sizing to prevent element overflow
  
- 📐 **Multiple Layout Directions**
  - Left-to-right layout (LR)
  - Top-to-bottom layout (TB)
  - Branch-aware positioning
  
- 🌈 **Colorful Arrow Labels**
  - Intelligent color mapping based on label semantics
  - Support for Chinese and English labels
  - Customizable color themes
  
- 📝 **Dual Format Support**
  - Full Mermaid syntax support with labeled arrows
  - Markdown list conversion
  - Automatic text type detection

- 🤖 **AI Flowchart Generation**
  - Select any available Dify LLM model directly in the tool
  - Convert plain text into clean Mermaid flowchart syntax
  - Choose top-bottom, left-right, or free layout output
  - Optionally download the AI-generated Mermaid source
  
- 🎭 **Rich Themes**
  - Modern theme with gradient effects
  - Business professional theme
  - Classic minimalist theme
  - Custom theme support
  
- 🔧 **Local Processing**
  - **Local Generation**: Flowcharts generated locally, no API Key required, no external network or services needed
  - **Secure & Reliable**: Data stays private, completely offline processing, protects user privacy
  - No external API dependencies
  - Fast generation with matplotlib
  - Privacy-focused design
  - High-quality PNG output

## 🚀 Quick Start

1. **Download from Dify Plugin Marketplace**
   - Go to Dify Plugin Marketplace
   - Search and download `flow_map` plugin
   - Enable FlowMap plugin in your workspace

2. **AI Flowchart** ⭐
   - Configure an available LLM model in Dify
   - Select the `ai_flow_map` / `AI Flowchart` tool
   - Choose the LLM model, paste plain text, and select the output layout
   - Run the tool to generate a PNG flowchart locally

3. **Manual LLM Integration**
   - Add an LLM node in your Dify workflow
   - Use the simplest prompt: **"Summarize user input #context# into Mermaid flowchart text format"**
   - Connect LLM output to FlowMap plugin input

### Basic Usage Examples
<img width="1883" height="884" alt="flow_map_en_a_01" src="https://github.com/user-attachments/assets/9de1c2c2-8952-4282-8d06-3a3448bef01a" />
<img width="2139" height="633" alt="flow_map_en_c_01" src="https://github.com/user-attachments/assets/655b0c59-3035-4936-ac1c-8f23c28c3210" />

**Top-to-bottom layout**
<img width="6453" height="5142" alt="flow_map_en_a_02" src="https://github.com/user-attachments/assets/52c7e645-4cd5-4fdd-a8df-c50b9740881e" />
<img width="15777" height="3418" alt="flow_map_en_c_03" src="https://github.com/user-attachments/assets/526ab72d-221d-40bc-be64-d402d2ae79e6" />

**Left-to-right layout**
<img width="6453" height="5142" alt="flow_map_en_a_03" src="https://github.com/user-attachments/assets/b969e429-45fb-40d5-987d-ce8bd4d8c02f" />
<img width="7667" height="6874" alt="flow_map_en_c_02" src="https://github.com/user-attachments/assets/5ed9b3b4-5ca1-4171-8c5f-f04654c6efd5" />

## 📚 API Reference

### AI Flowchart Tool

**Input Parameters:**
- `model_config` (model-selector, required): LLM model selected in Dify
- `text_content` (string, required): Plain text to summarize into a flowchart
- `layout_mode` (string, optional): `top_bottom`, `left_right`, or `free`
- `theme` (string, optional): Theme name (modern/business/classic/tech/minimal)
- `filename` (string, optional): Base filename for the downloadable Mermaid source
- `download_mermaid` (boolean, optional): Output the AI-generated Mermaid file

**Output:**
- Success: PNG image + text summary + JSON details
- Optional: Mermaid source file when `download_mermaid=true`
- JSON includes `layout_mode`, `theme`, and `generated_mermaid`

### Mermaid Left-Right Tool

**Input Parameters:**
- `text` (string, required): Mermaid syntax flowchart text
- `theme` (string, optional): Theme name (modern/business/classic)

**Output:**
- Success: PNG image + text summary
- Format: "Successfully generated left-right layout flowchart. File size: X.XXM. Contains X nodes and X connections."

### Mermaid Top-Bottom Tool

**Input Parameters:**
- `text` (string, required): Mermaid syntax flowchart text
- `theme` (string, optional): Theme name (modern/business/classic)

**Output:**
- Success: PNG image + text summary
- Format: "Successfully generated top-bottom layout flowchart. File size: X.XXM. Contains X nodes and X connections."

## 🛠️ Advanced Features

### Smart Branch Detection

The plugin automatically detects branching scenarios in your flowchart and switches layout algorithms:

- **Linear Flow**: Uses grid layout for optimal alignment
- **Branching Flow**: Uses free layout to prevent overlap
- **Complex Flow**: Automatically expands spacing and uses Bezier curve routing with orthogonal fallback to reduce line interference in dense free-layout diagrams

### Colorful Arrow Labels

Supports labeled arrows with intelligent color mapping

### Theme Customization

Available themes with different visual styles:

- **Modern**: Clean design with gradients
- **Business**: Professional corporate style
- **Classic**: Traditional minimalist look

## 🔧 Development

### Project Structure

```
flow_map/
├── tools/                  # Core tools implementation
│   ├── ai_flow_map.py      # AI text-to-flowchart tool
│   ├── mermaid_lr.py      # Left-right layout tool
│   ├── mermaid_tb.py      # Top-bottom layout tool
│   ├── mermaid_free.py    # Free layout tool
│   └── optimized_layout.py # Advanced layout engine
├── provider/              # Provider configurations
├── test/                  # Comprehensive tests
├── manifest.yaml          # Plugin manifest
├── main.py               # Entry point
└── README.md             # Documentation
```


## 🔍 Technical Details

### Branch-Aware Layout Algorithm

- **Branch Detection**: Automatically identifies decision nodes with multiple outgoing connections
- **Free Layout**: Hierarchical positioning based on connection levels
- **Canvas Adaptation**: Dynamic canvas sizing (up to 2.5x node count)
- **Collision Avoidance**: Smart spacing with 70% effective area usage
- **Complex Routing**: Dense free-layout flowcharts use Bezier curve fan-out, per-edge channel offsets, orthogonal fallback, canvas-bounded routing, and label collision avoidance

### Performance Optimization

- **Matplotlib Backend**: High-quality vector graphics
- **Memory Efficient**: Local processing without external APIs
- **Fast Rendering**: Optimized for complex flowcharts

## Developer Information

- **Author**: [@sawyer-shi](https://github.com/sawyer-shi)
- **Email**: sawyer36@foxmail.com 【Currently looking for new job opportunities】
- **License**: MIT License
- **Source Code**: https://github.com/sawyer-shi/dify-plugins-flow_map
- **Support**: Through Dify platform, GitHub Issues, and email

## License Notice

This project is licensed under the MIT License.


---

**Ready to create beautiful flowcharts?**
