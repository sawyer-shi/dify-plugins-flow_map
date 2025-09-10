# -*- coding: utf-8 -*-
"""
Flow Map Generator Demo
流程图生成器演示

This script demonstrates the capabilities of the FlowMapGenerator.
该脚本演示FlowMapGenerator的功能。
"""

import os
import base64
import matplotlib
matplotlib.use('Agg')

from tools.flow_map import FlowMapGenerator


def save_image(image_base64: str, filename: str):
    """Save base64 image to file / 将base64图片保存到文件"""
    image_data = base64.b64decode(image_base64)
    with open(filename, 'wb') as f:
        f.write(image_data)
    print(f"✓ Saved image to {filename}")


def demo_markdown_examples():
    """Demonstrate Markdown flowchart generation / 演示Markdown流程图生成"""
    print("=" * 60)
    print("Markdown Flowchart Examples / Markdown流程图示例")
    print("=" * 60)
    
    generator = FlowMapGenerator()
    
    # Example 1: Simple Process Flow / 示例1：简单流程
    print("\n1. Simple Process Flow / 简单流程:")
    markdown_text1 = """
    # User Registration Process
    1. Start registration
    2. Enter user information
    3. Validate input data?
    4. Process registration
    5. Send confirmation email
    6. Complete registration
    """
    
    result = generator.from_markdown(markdown_text1, "left-right")
    if result["success"]:
        save_image(result["image"], "demo_markdown_simple.png")
        print(f"   Nodes: {result['nodes_count']}, Connections: {result['connections_count']}")
    
    # Example 2: Decision Flow / 示例2：决策流程
    print("\n2. Decision Flow / 决策流程:")
    markdown_text2 = """
    - Begin process
    - Check user permissions?
    - Access granted
    - Execute operation
    - Log activity
    - End process
    """
    
    result = generator.from_markdown(markdown_text2, "top-bottom")
    if result["success"]:
        save_image(result["image"], "demo_markdown_decision.png")
        print(f"   Nodes: {result['nodes_count']}, Connections: {result['connections_count']}")
    
    # Example 3: Chinese Content / 示例3：中文内容
    print("\n3. Chinese Content / 中文内容:")
    chinese_text = """
    # 订单处理流程
    1. 开始处理订单
    2. 验证订单信息
    3. 检查库存是否充足？
    4. 生成发货单
    5. 安排物流配送
    6. 完成订单处理
    """
    
    result = generator.from_markdown(chinese_text, "left-right")
    if result["success"]:
        save_image(result["image"], "demo_markdown_chinese.png")
        print(f"   Nodes: {result['nodes_count']}, Connections: {result['connections_count']}")


def demo_mermaid_examples():
    """Demonstrate Mermaid flowchart generation / 演示Mermaid流程图生成"""
    print("\n" + "=" * 60)
    print("Mermaid Flowchart Examples / Mermaid流程图示例")
    print("=" * 60)
    
    generator = FlowMapGenerator()
    
    # Example 1: Basic Mermaid Flow / 示例1：基本Mermaid流程
    print("\n1. Basic Mermaid Flow / 基本Mermaid流程:")
    mermaid_text1 = """
    graph TD
        A[Start] --> B{Check Status}
        B -->|Valid| C[Process]
        B -->|Invalid| D[Error]
        C --> E[Success]
        D --> F[End]
        E --> F
    """
    
    result = generator.from_mermaid(mermaid_text1, "top-bottom")
    if result["success"]:
        save_image(result["image"], "demo_mermaid_basic.png")
        print(f"   Nodes: {result['nodes_count']}, Connections: {result['connections_count']}")
    
    # Example 2: Complex Workflow / 示例2：复杂工作流
    print("\n2. Complex Workflow / 复杂工作流:")
    mermaid_text2 = """
    graph LR
        A[User Input] --> B{Validate}
        B --> C[Database Check]
        C --> D{Exists?}
        D -->|Yes| E[Update]
        D -->|No| F[Create]
        E --> G[Response]
        F --> G
    """
    
    result = generator.from_mermaid(mermaid_text2, "left-right")
    if result["success"]:
        save_image(result["image"], "demo_mermaid_complex.png")
        print(f"   Nodes: {result['nodes_count']}, Connections: {result['connections_count']}")


def demo_tool_integration():
    """Demonstrate FlowMapTool integration / 演示FlowMapTool集成"""
    print("\n" + "=" * 60)
    print("Tool Integration Demo / 工具集成演示")
    print("=" * 60)
    
    from tools.flow_map import FlowMapTool
    
    tool = FlowMapTool()
    
    # Test tool with different parameters / 使用不同参数测试工具
    test_cases = [
        {
            "name": "Markdown Left-Right",
            "params": {
                "text": "1. Start\n2. Process\n3. Decision?\n4. End",
                "format": "markdown",
                "layout": "left-right"
            }
        },
        {
            "name": "Mermaid Top-Bottom", 
            "params": {
                "text": "graph TD\nA[Begin] --> B[Finish]",
                "format": "mermaid",
                "layout": "top-bottom"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}:")
        messages = list(tool._invoke(test_case['params']))
        
        if messages:
            import json
            result = json.loads(messages[0].message)
            if result["success"]:
                save_image(result["image"], f"demo_tool_{i}.png")
                print(f"   ✓ Generated successfully with {result['nodes_count']} nodes")
            else:
                print(f"   ✗ Failed: {result.get('error', 'Unknown error')}")


def main():
    """Main demo function / 主演示函数"""
    print("🎨 Flow Map Generator Demo / 流程图生成器演示")
    print("This demo will generate several example flowcharts.")
    print("该演示将生成几个示例流程图。")
    
    # Create output directory if it doesn't exist / 如果不存在则创建输出目录
    os.makedirs("demo_output", exist_ok=True)
    os.chdir("demo_output")
    
    try:
        # Run demonstrations / 运行演示
        demo_markdown_examples()
        demo_mermaid_examples()
        demo_tool_integration()
        
        print("\n" + "=" * 60)
        print("🎉 Demo completed successfully! / 演示成功完成！")
        print("Check the 'demo_output' folder for generated images.")
        print("请查看'demo_output'文件夹中的生成图片。")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
