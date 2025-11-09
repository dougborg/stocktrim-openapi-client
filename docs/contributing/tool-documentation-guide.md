# Auto-Generation Implementation Guide

This guide demonstrates how to implement auto-generation utilities for tool
documentation in the StockTrim MCP server.

## 1. Docstring Parser Utility

### Location

`stocktrim_mcp_server/src/stocktrim_mcp_server/utils/docstring_parser.py`

### Implementation Example

```python
import re
from dataclasses import dataclass, field

@dataclass
class DocstringSection:
    """Parsed section of a docstring."""
    name: str
    content: str
    items: dict[str, str] = field(default_factory=dict)  # For Args/Returns sections

class DocstringParser:
    """Parse tool docstrings following Google-style format."""

    def __init__(self, docstring: str):
        self.docstring = docstring
        self.summary = ""
        self.description = ""
        self.args = {}
        self.returns = ""
        self.example = ""
        self.see_also = []
        self._parse()

    def _parse(self):
        """Parse docstring into sections."""
        lines = self.docstring.split('\n')

        # Extract summary (first non-empty line)
        for i, line in enumerate(lines):
            if line.strip():
                self.summary = line.strip()
                remaining_lines = lines[i+1:]
                break

        # Split into sections
        current_section = None
        current_content = []

        for line in remaining_lines:
            # Check for section headers (## or standard format)
            if re.match(r'^##?\s+(\w+)', line):
                if current_section:
                    self._process_section(current_section, current_content)
                current_section = re.match(r'^##?\s+(\w+)', line).group(1)
                current_content = []
            elif line.startswith('Args:') or line.startswith('Returns:'):
                if current_section:
                    self._process_section(current_section, current_content)
                current_section = line.rstrip(':')
                current_content = []
            else:
                current_content.append(line)

        if current_section:
            self._process_section(current_section, current_content)

    def _process_section(self, section_name: str, content: list[str]):
        """Process a docstring section."""
        text = '\n'.join(content).strip()

        if section_name == 'Args':
            self.args = self._parse_args(content)
        elif section_name == 'Returns':
            self.returns = text
        elif section_name == 'Example':
            self.example = text
        elif section_name == 'See Also':
            self.see_also = self._parse_see_also(content)
        elif section_name == 'How It Works':
            self.description += '\n' + text
        else:
            self.description += '\n' + text

    def _parse_args(self, lines: list[str]) -> dict[str, str]:
        """Extract argument descriptions from Args section."""
        args = {}
        current_arg = None
        current_desc = []

        for line in lines:
            # Match "    arg_name: description"
            match = re.match(r'^\s+(\w+):\s*(.*)', line)
            if match:
                if current_arg:
                    args[current_arg] = ' '.join(current_desc).strip()
                current_arg = match.group(1)
                current_desc = [match.group(2)] if match.group(2) else []
            elif current_arg and line.strip():
                current_desc.append(line.strip())

        if current_arg:
            args[current_arg] = ' '.join(current_desc).strip()

        return args

    def _parse_see_also(self, lines: list[str]) -> list[str]:
        """Extract related tools from See Also section."""
        tools = []
        for line in lines:
            # Match "- `tool_name`:" or "- tool_name:"
            match = re.search(r'`?(\w+)`?', line)
            if match:
                tools.append(match.group(1))
        return tools

    @classmethod
    def from_function(cls, fn) -> 'DocstringParser':
        """Create parser from a function."""
        import inspect
        docstring = inspect.getdoc(fn) or ""
        return cls(docstring)
```

### Usage Example

```python
from docstring_parser import DocstringParser
from tools.foundation.customers import get_customer

parser = DocstringParser.from_function(get_customer)
print(parser.summary)       # "Get a customer by code."
print(parser.args)         # {"request": "Request containing customer code", ...}
print(parser.returns)      # "CustomerInfo if found, None if not found"
print(parser.example)      # JSON example
```

______________________________________________________________________

## 2. Tool Metadata Extractor

### Location

`stocktrim_mcp_server/src/stocktrim_mcp_server/utils/tool_metadata.py`

### Implementation Example

```python
import inspect
import json
import re
from dataclasses import dataclass, asdict, field
from typing import Any, Callable, get_type_hints
from pydantic import BaseModel

@dataclass
class ParameterMetadata:
    """Metadata for a tool parameter."""
    name: str
    type_: str
    description: str
    required: bool
    default_value: Any = None

@dataclass
class ToolMetadata:
    """Complete metadata for a tool."""
    name: str
    category: str  # 'foundation' or 'workflow'
    type_: str     # 'get', 'list', 'create', 'update', 'delete', 'review', 'generate'
    summary: str
    description: str
    parameters: list[ParameterMetadata]
    return_type: str
    risk_level: str  # 'low', 'medium', 'high'
    examples: list[dict] = field(default_factory=list)
    related_tools: list[str] = field(default_factory=list)

class ToolMetadataExtractor:
    """Extract metadata from tool functions."""

    RISK_KEYWORDS = {
        'delete': 'high',
        'remove': 'high',
        'destroy': 'high',
        'permanently': 'high',
        'update': 'medium',
        'modify': 'medium',
        'change': 'medium',
        'get': 'low',
        'list': 'low',
        'retrieve': 'low',
        'query': 'low',
    }

    CATEGORY_PATTERNS = {
        'workflow': ['review_', 'generate_', 'update_and_', 'manage_', 'create_with_'],
        'foundation': ['get_', 'list_', 'create_', 'update_', 'delete_', 'set_'],
    }

    TYPE_PATTERNS = {
        'get': r'^get_',
        'list': r'^list_',
        'create': r'^create_',
        'update': r'^update_',
        'delete': r'^delete_',
        'review': r'^review_',
        'generate': r'^generate_',
    }

    def __init__(self, tool_fn: Callable):
        self.fn = tool_fn
        self.name = tool_fn.__name__
        self.sig = inspect.signature(tool_fn)
        self.docstring_parser = self._parse_docstring()
        self.request_model = self._get_request_model()
        self.return_type = self._get_return_type()

    def _parse_docstring(self):
        """Parse tool docstring."""
        from docstring_parser import DocstringParser
        return DocstringParser.from_function(self.fn)

    def _get_request_model(self) -> type[BaseModel] | None:
        """Get the request model from function signature."""
        params = self.sig.parameters
        for param in params.values():
            if param.annotation != inspect.Parameter.empty:
                annotation = param.annotation
                if isinstance(annotation, type) and issubclass(annotation, BaseModel):
                    return annotation
        return None

    def _get_return_type(self) -> str:
        """Get return type as string."""
        return_annotation = self.sig.return_annotation
        if return_annotation == inspect.Parameter.empty:
            return "None"
        if hasattr(return_annotation, '__name__'):
            return return_annotation.__name__
        return str(return_annotation)

    def _extract_parameters(self) -> list[ParameterMetadata]:
        """Extract parameter metadata from request model."""
        params = []

        if not self.request_model:
            return params

        # Get field info from Pydantic model
        for field_name, field_info in self.request_model.model_fields.items():
            param = ParameterMetadata(
                name=field_name,
                type_=str(field_info.annotation),
                description=field_info.description or "",
                required=field_info.is_required(),
                default_value=field_info.default if not field_info.is_required() else None,
            )
            params.append(param)

        return params

    def _detect_category(self) -> str:
        """Detect tool category from name."""
        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if self.name.startswith(pattern):
                    return category
        return 'foundation'

    def _detect_type(self) -> str:
        """Detect tool type from name."""
        for type_, pattern in self.TYPE_PATTERNS.items():
            if re.match(pattern, self.name):
                return type_
        return 'workflow'

    def _detect_risk_level(self) -> str:
        """Detect risk level from docstring and name."""
        # Check docstring for risk indicators
        full_text = (self.docstring_parser.summary + ' ' +
                     self.docstring_parser.description).lower()

        for keyword, level in self.RISK_KEYWORDS.items():
            if keyword in full_text:
                return level

        # Default based on type
        if self.name.startswith('delete_'):
            return 'high'
        elif self.name.startswith(('update_', 'create_')):
            return 'medium'

        return 'low'

    def extract(self) -> ToolMetadata:
        """Extract all metadata from tool."""
        return ToolMetadata(
            name=self.name,
            category=self._detect_category(),
            type_=self._detect_type(),
            summary=self.docstring_parser.summary,
            description=self.docstring_parser.description,
            parameters=self._extract_parameters(),
            return_type=self.return_type,
            risk_level=self._detect_risk_level(),
            related_tools=self.docstring_parser.see_also or [],
        )

class ToolMetadataCollector:
    """Collect metadata from all tools in the system."""

    def __init__(self, tools_dir: str):
        self.tools_dir = tools_dir
        self.metadata: list[ToolMetadata] = []

    def collect_from_module(self, module) -> list[ToolMetadata]:
        """Collect metadata from a tools module."""
        tools = []

        for name, obj in inspect.getmembers(module):
            if inspect.iscoroutinefunction(obj) and not name.startswith('_'):
                try:
                    extractor = ToolMetadataExtractor(obj)
                    metadata = extractor.extract()
                    tools.append(metadata)
                except Exception as e:
                    print(f"Failed to extract metadata for {name}: {e}")

        return tools

    def to_json(self) -> str:
        """Export all metadata as JSON."""
        data = [asdict(m) for m in self.metadata]
        return json.dumps(data, indent=2, default=str)

    def to_markdown(self) -> str:
        """Export all metadata as markdown."""
        lines = ["# Tool Reference\n"]

        # Group by category
        by_category = {}
        for tool in self.metadata:
            if tool.category not in by_category:
                by_category[tool.category] = []
            by_category[tool.category].append(tool)

        for category in ['foundation', 'workflow']:
            if category not in by_category:
                continue

            lines.append(f"\n## {category.title()} Tools\n")

            for tool in sorted(by_category[category], key=lambda t: t.name):
                # Tool header
                risk_emoji = self._risk_emoji(tool.risk_level)
                lines.append(f"### `{tool.name}` {risk_emoji}\n")

                # Description
                lines.append(f"{tool.summary}\n")
                if tool.description:
                    lines.append(f"{tool.description}\n")

                # Parameters
                if tool.parameters:
                    lines.append("**Parameters:**\n")
                    lines.append("| Name | Type | Required | Description |")
                    lines.append("|------|------|----------|-------------|")
                    for param in tool.parameters:
                        req = "Yes" if param.required else "No"
                        lines.append(
                            f"| `{param.name}` | {param.type_} | {req} | {param.description} |"
                        )
                    lines.append("")

                # Returns
                if tool.return_type:
                    lines.append(f"**Returns:** `{tool.return_type}`\n")

                # Related tools
                if tool.related_tools:
                    lines.append("**Related Tools:**\n")
                    for related in tool.related_tools:
                        lines.append(f"- `{related}`")
                    lines.append("")

        return '\n'.join(lines)

    @staticmethod
    def _risk_emoji(level: str) -> str:
        """Get emoji for risk level."""
        return {
            'low': '🟢',
            'medium': '🟡',
            'high': '🔴',
        }.get(level, '')
```

### Usage Example

```python
from tool_metadata import ToolMetadataExtractor, ToolMetadataCollector
from stocktrim_mcp_server.tools.foundation import customers

# Extract metadata from single tool
extractor = ToolMetadataExtractor(customers.get_customer)
metadata = extractor.extract()
print(metadata.name)        # "get_customer"
print(metadata.risk_level)  # "low"
print(metadata.parameters)  # [ParameterMetadata(...), ...]

# Collect from all tools
collector = ToolMetadataCollector("stocktrim_mcp_server/tools")
# ... collect from all modules ...

# Export as markdown
with open("docs/mcp-server/tools_generated.md", "w") as f:
    f.write(collector.to_markdown())
```

______________________________________________________________________

## 3. Field Description Auto-Generator

### Location

`stocktrim_mcp_server/src/stocktrim_mcp_server/utils/field_generator.py`

### Implementation Example

```python
import re
from typing import Type
from pydantic import BaseModel, Field, create_model
from pydantic.fields import FieldInfo

def generate_field_descriptions_from_docstring(
    fn: Callable,
    request_model: Type[BaseModel]
) -> dict[str, FieldInfo]:
    """
    Generate Field descriptions from function docstring Args section.

    Example:
        Given docstring with:
            Args:
                request: Contains:
                    - code: Unique identifier
                    - name: Display name

        Will generate Field(description="...") for each parameter.
    """
    from docstring_parser import DocstringParser

    parser = DocstringParser.from_function(fn)
    new_fields = {}

    for field_name, field_info in request_model.model_fields.items():
        # Check if we have docstring description for this field
        if field_name in parser.args:
            docstring_desc = parser.args[field_name]

            # Create new FieldInfo with docstring description
            # while preserving other constraints
            new_fields[field_name] = Field(
                default=field_info.default if not field_info.is_required() else ...,
                description=docstring_desc,
                # Preserve constraints
                **{
                    k: v for k, v in field_info._attributes_set.items()
                    if k not in ['description', 'default']
                }
            )
        else:
            new_fields[field_name] = field_info

    return new_fields

def create_documented_request_model(
    fn: Callable,
    existing_model: Type[BaseModel],
    new_name: str = None
) -> Type[BaseModel]:
    """
    Create a new request model with descriptions from docstring.

    Usage:
        # Instead of:
        class CreateProductRequest(BaseModel):
            code: str = Field(..., description="...")
            name: str = Field(..., description="...")

        # Do:
        NewRequest = create_documented_request_model(
            create_product,
            CreateProductRequest,
            "DocumentedCreateProductRequest"
        )
    """
    fields = generate_field_descriptions_from_docstring(fn, existing_model)
    model_name = new_name or f"Documented{existing_model.__name__}"

    return create_model(
        model_name,
        __base__=existing_model,
        **{name: (field_info.annotation, field_info)
           for name, field_info in fields.items()}
    )
```

______________________________________________________________________

## 4. Tool Registration Metadata Hook

### Location

`stocktrim_mcp_server/src/stocktrim_mcp_server/tools/registration.py`

### Implementation Example

```python
from typing import Callable, Optional
from fastmcp import FastMCP
from tool_metadata import ToolMetadataExtractor, ToolMetadata

class ToolRegistry:
    """Registry with built-in metadata extraction."""

    def __init__(self, mcp: FastMCP):
        self.mcp = mcp
        self.tools: list[tuple[str, Callable, Optional[ToolMetadata]]] = []

    def register_tool(
        self,
        fn: Callable,
        extract_metadata: bool = True
    ) -> Callable:
        """Register a tool and optionally extract metadata."""

        # Register with FastMCP
        self.mcp.tool()(fn)

        # Extract metadata
        metadata = None
        if extract_metadata:
            try:
                extractor = ToolMetadataExtractor(fn)
                metadata = extractor.extract()
            except Exception as e:
                print(f"Failed to extract metadata for {fn.__name__}: {e}")

        # Store for later access
        self.tools.append((fn.__name__, fn, metadata))

        return fn

    def get_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """Get metadata for a registered tool."""
        for name, _, metadata in self.tools:
            if name == tool_name:
                return metadata
        return None

    def export_metadata_json(self) -> str:
        """Export all metadata as JSON."""
        import json
        from dataclasses import asdict

        data = []
        for name, _, metadata in self.tools:
            if metadata:
                data.append(asdict(metadata))

        return json.dumps(data, indent=2, default=str)

# Usage in tool modules:
def register_tools(mcp: FastMCP) -> None:
    """Register customer tools with metadata extraction."""
    registry = ToolRegistry(mcp)

    registry.register_tool(get_customer)
    registry.register_tool(list_customers)
    registry.register_tool(create_customer)
```

______________________________________________________________________

## 5. Testing Auto-Generated Documentation

### Location

`stocktrim_mcp_server/tests/test_utils/test_tool_metadata.py`

### Implementation Example

```python
import pytest
from utils.tool_metadata import ToolMetadataExtractor
from tools.foundation.customers import get_customer, list_customers, GetCustomerRequest

class TestToolMetadataExtraction:

    def test_extract_basic_metadata(self):
        """Test extracting metadata from simple get tool."""
        extractor = ToolMetadataExtractor(get_customer)
        metadata = extractor.extract()

        assert metadata.name == "get_customer"
        assert metadata.category == "foundation"
        assert metadata.type_ == "get"
        assert metadata.risk_level == "low"
        assert len(metadata.parameters) > 0

    def test_extract_parameter_descriptions(self):
        """Test that parameter descriptions are extracted."""
        extractor = ToolMetadataExtractor(get_customer)
        metadata = extractor.extract()

        # Should have 'code' parameter from request model
        code_param = next(
            (p for p in metadata.parameters if p.name == "code"),
            None
        )
        assert code_param is not None
        assert code_param.description != ""
        assert not code_param.required or code_param.default_value is None

    def test_detect_high_risk_tools(self):
        """Test that delete operations are marked as high-risk."""
        from tools.foundation.products import delete_product

        extractor = ToolMetadataExtractor(delete_product)
        metadata = extractor.extract()

        assert metadata.risk_level == "high"
        assert "delete" in metadata.summary.lower()

    def test_docstring_parsing(self):
        """Test that docstrings are properly parsed."""
        extractor = ToolMetadataExtractor(list_customers)

        assert extractor.docstring_parser.summary != ""
        assert extractor.docstring_parser.returns != ""

    def test_export_to_json(self):
        """Test JSON export of metadata."""
        from tool_metadata import ToolMetadataCollector
        import json

        collector = ToolMetadataCollector(".")
        extractor = ToolMetadataExtractor(get_customer)
        collector.metadata.append(extractor.extract())

        json_str = collector.to_json()
        data = json.loads(json_str)

        assert len(data) == 1
        assert data[0]['name'] == 'get_customer'
```

______________________________________________________________________

## 6. Integration with Build Process

### Location

`stocktrim_mcp_server/scripts/generate_tool_docs.py`

### Implementation Example

```python
#!/usr/bin/env python3
"""Generate tool documentation from source code."""

import argparse
import sys
from pathlib import Path
from tool_metadata import ToolMetadataCollector

def main():
    parser = argparse.ArgumentParser(description="Generate tool documentation")
    parser.add_argument(
        "--output",
        "-o",
        default="docs/mcp-server/tools_auto.md",
        help="Output file for generated documentation"
    )
    parser.add_argument(
        "--json",
        "-j",
        help="Also export metadata as JSON"
    )

    args = parser.parse_args()

    # Collect metadata from all tools
    collector = ToolMetadataCollector("stocktrim_mcp_server/tools")

    # Import all tool modules to collect metadata
    import importlib

    tool_modules = [
        'stocktrim_mcp_server.tools.foundation.customers',
        'stocktrim_mcp_server.tools.foundation.products',
        'stocktrim_mcp_server.tools.foundation.suppliers',
        # ... etc
    ]

    for module_name in tool_modules:
        try:
            module = importlib.import_module(module_name)
            collector.metadata.extend(collector.collect_from_module(module))
        except Exception as e:
            print(f"Failed to collect from {module_name}: {e}")

    # Generate markdown documentation
    markdown = collector.to_markdown()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown)

    print(f"Generated documentation for {len(collector.metadata)} tools")
    print(f"Saved to: {output_path}")

    # Export JSON if requested
    if args.json:
        json_path = Path(args.json)
        json_path.write_text(collector.to_json())
        print(f"Saved JSON metadata to: {json_path}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Usage in CI/CD

```bash
# In pre-commit hook or CI pipeline
python stocktrim_mcp_server/scripts/generate_tool_docs.py \
    --output docs/mcp-server/tools_generated.md \
    --json docs/mcp-server/tools_metadata.json
```

______________________________________________________________________

## 7. Summary of Auto-Generation Opportunities

The above implementation provides:

1. **Docstring Parsing** (220 lines) - Extracts documentation from Google-style
   docstrings
1. **Metadata Extraction** (280 lines) - Builds complete tool metadata including risk
   detection
1. **Field Description Generation** (60 lines) - Auto-populates Pydantic Field
   descriptions
1. **Tool Registry Hook** (80 lines) - Integrates with tool registration process
1. **Test Suite** (120 lines) - Validates auto-generated content
1. **Build Integration** (90 lines) - Generates documentation during build

**Total LOC**: ~850 lines to implement comprehensive auto-generation

**Benefits**:

- Single source of truth (docstrings)
- Automatic risk level detection
- Generated markdown documentation
- JSON metadata export for tooling
- Validated parameter descriptions
- Tool categorization and linking
