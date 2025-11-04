# 插件开发指南

## 扩展 create_plan 工具参数

### 概述

插件可以通过 `hook_extend_create_plan_params` 扩展 `create_plan` 工具的参数，让 LLM 在生成大纲时能够填写更多自定义字段。

### 基础用法

```python
from typing import Dict, Any, Optional, List
from backend.plugins import hookimpl

class MyPlugin:
    
    @hookimpl
    def hook_extend_create_plan_params(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """扩展 create_plan 工具的参数"""
        return {
            "world_setting": {
                "type": str,
                "description": "世界观设定",
                "required": False  # 可选参数
            },
            "key_items": {
                "type": List[str],
                "description": "本章出现的关键物品",
                "required": False
            },
            "location": {
                "type": str,
                "description": "主要场景地点",
                "required": False
            }
        }
```

### 参数定义格式

每个参数定义包含以下字段：

```python
{
    "param_name": {
        "type": type,          # Python 类型：str, int, List[str], Dict[str, Any] 等
        "description": "描述",  # 参数描述，LLM 会看到这个
        "required": False      # 是否必填，默认 False
    }
}
```

### 支持的类型

- **基础类型**: `str`, `int`, `float`, `bool`
- **列表**: `List[str]`, `List[int]` 等
- **字典**: `Dict[str, Any]`, `Dict[str, str]` 等
- **可选类型**: `Optional[str]` 等

### 输出格式

插件扩展的参数会自动追加到生成的 plan 中：

```markdown
# 章节标题

## 主要情节点
1. 情节点1
2. 情节点2

## 涉及角色
角色A, 角色B

## 情节推进方向
...

## 重要场景
...

## 世界观设定
这是插件扩展的内容

## 本章出现的关键物品
- 物品1
- 物品2

## 主要场景地点
某个地方
```

### 完整示例

```python
from typing import Dict, Any, Optional, List
from backend.plugins import hookimpl

class WorldBuildingPlugin:
    """世界观管理插件"""
    
    name = "WorldBuildingPlugin"
    description = "管理小说的世界观设定"
    version = "1.0.0"
    
    @hookimpl
    def hook_extend_create_plan_params(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """扩展 create_plan 参数"""
        return {
            "world_setting": {
                "type": str,
                "description": "世界观设定（魔法体系、科技水平等）",
                "required": False
            },
            "power_system": {
                "type": Dict[str, str],
                "description": "力量体系说明",
                "required": False
            },
            "time_period": {
                "type": str,
                "description": "时间线位置",
                "required": False
            },
            "key_locations": {
                "type": List[str],
                "description": "关键地点",
                "required": False
            },
            "key_items": {
                "type": List[str],
                "description": "关键物品/道具",
                "required": False
            },
            "foreshadowing": {
                "type": List[str],
                "description": "本章埋下的伏笔",
                "required": False
            }
        }
    
    @hookimpl
    def hook_inject_system_prompt(self, stage: str, context: Dict[str, Any]) -> Optional[str]:
        """提示 LLM 使用扩展参数"""
        if stage == "plan":
            return """
在规划大纲时，请特别注意：
1. 明确本章涉及的世界观元素
2. 标记出现的关键物品和地点
3. 记录埋下的伏笔，为后续剧情做准备
4. 说明时间线位置，保持时间连贯性
"""
        return None
```

### 最佳实践

1. **描述清晰**: `description` 要写清楚，LLM 依赖这个来理解参数用途
2. **类型明确**: 使用正确的类型，帮助 LLM 生成正确格式的数据
3. **非必填**: 大部分扩展参数应该是 `required: False`，避免打断对话流程
4. **配合提示词**: 通过 `hook_inject_system_prompt` 提示 LLM 使用这些参数
5. **后处理**: 可以在 `hook_after_plan` 中解析和使用这些扩展参数

### 注意事项

- 参数名不要和基础参数冲突（`title`, `plot_points`, `characters`, `direction`, `scenes`）
- 如果多个插件定义了同名参数，后注册的会覆盖先注册的
- LLM 可能不会总是填写所有扩展参数，要做好空值处理

### 调试

在 plan 生成后，可以在 `hook_after_plan` 中查看完整的 plan 内容：

```python
@hookimpl
def hook_after_plan(self, plan: str, context: Dict[str, Any]) -> Optional[str]:
    print(f"生成的 plan:\n{plan}")
    # 可以解析和验证扩展参数是否被正确填写
    return None
```

