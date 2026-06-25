import os
from typing import List, Dict, Optional, Any
import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_typescript
import tree_sitter_java
from tree_sitter import Language, Parser, Node

class UnsupportedLanguageError(Exception):
    """Raised when an unsupported language is provided for AST chunking."""
    pass

PY_LANGUAGE = Language(tree_sitter_python.language())
JS_LANGUAGE = Language(tree_sitter_javascript.language())
TS_LANGUAGE = Language(tree_sitter_typescript.language_typescript())
JAVA_LANGUAGE = Language(tree_sitter_java.language())

def get_parser(language: str) -> Optional[Parser]:
    """Get the appropriate tree-sitter parser for the given language."""
    if language == "Python":
        return Parser(PY_LANGUAGE)
    elif language == "JavaScript":
        return Parser(JS_LANGUAGE)
    elif language == "TypeScript":
        return Parser(TS_LANGUAGE)
    elif language == "Java":
        return Parser(JAVA_LANGUAGE)
    return None

def extract_node_text(node: Node, source_bytes: bytes) -> str:
    """Extract the exact text of a node from the source bytes."""
    return source_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='replace')

def extract_python_chunks(root_node: Node, source_bytes: bytes, file_path: str) -> List[Dict[str, Any]]:
    """Extract chunks from a Python syntax tree."""
    chunks = []
    
    # Extract module docstring
    if root_node.children:
        first_child = root_node.children[0]
        if first_child.type == "expression_statement":
            expr = first_child.children[0]
            if expr.type == "string":
                chunks.append({
                    "file_path": file_path,
                    "start_line": first_child.start_point[0] + 1,
                    "end_line": first_child.end_point[0] + 1,
                    "language": "Python",
                    "chunk_type": "docstring",
                    "function_name": None,
                    "parent_class": None,
                    "source_code": extract_node_text(first_child, source_bytes)
                })

    def traverse(node: Node, parent_class: Optional[str] = None):
        if node.type == "class_definition":
            class_name_node = node.child_by_field_name("name")
            class_name = extract_node_text(class_name_node, source_bytes) if class_name_node else None
            chunks.append({
                "file_path": file_path,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "language": "Python",
                "chunk_type": "class",
                "function_name": None,
                "parent_class": parent_class,
                "source_code": extract_node_text(node, source_bytes)
            })
            
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    traverse(child, class_name)
                    
        elif node.type == "function_definition":
            func_name_node = node.child_by_field_name("name")
            func_name = extract_node_text(func_name_node, source_bytes) if func_name_node else None
            chunks.append({
                "file_path": file_path,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "language": "Python",
                "chunk_type": "function",
                "function_name": func_name,
                "parent_class": parent_class,
                "source_code": extract_node_text(node, source_bytes)
            })
        else:
            for child in node.children:
                traverse(child, parent_class)

    traverse(root_node)
    return chunks

def extract_javascript_chunks(root_node: Node, source_bytes: bytes, file_path: str) -> List[Dict[str, Any]]:
    """Extract chunks from a JavaScript syntax tree."""
    chunks = []
    
    def get_arrow_func_name(node: Node) -> Optional[str]:
        if node.parent and node.parent.type == "variable_declarator":
            name_node = node.parent.child_by_field_name("name")
            if name_node:
                return extract_node_text(name_node, source_bytes)
        if node.parent and node.parent.type == "assignment_expression":
            left_node = node.parent.child_by_field_name("left")
            if left_node:
                return extract_node_text(left_node, source_bytes)
        return None

    def traverse(node: Node, parent_class: Optional[str] = None):
        if node.type == "class_declaration":
            class_name_node = node.child_by_field_name("name")
            class_name = extract_node_text(class_name_node, source_bytes) if class_name_node else None
            chunks.append({
                "file_path": file_path,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "language": "JavaScript",
                "chunk_type": "class",
                "function_name": None,
                "parent_class": parent_class,
                "source_code": extract_node_text(node, source_bytes)
            })
            
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    traverse(child, class_name)
                    
        elif node.type == "method_definition":
            method_name_node = node.child_by_field_name("name")
            method_name = extract_node_text(method_name_node, source_bytes) if method_name_node else None
            chunks.append({
                "file_path": file_path,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "language": "JavaScript",
                "chunk_type": "function",
                "function_name": method_name,
                "parent_class": parent_class,
                "source_code": extract_node_text(node, source_bytes)
            })
            
        elif node.type == "function_declaration":
            func_name_node = node.child_by_field_name("name")
            func_name = extract_node_text(func_name_node, source_bytes) if func_name_node else None
            chunks.append({
                "file_path": file_path,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "language": "JavaScript",
                "chunk_type": "function",
                "function_name": func_name,
                "parent_class": parent_class,
                "source_code": extract_node_text(node, source_bytes)
            })
            
        elif node.type == "arrow_function":
            arrow_name = get_arrow_func_name(node)
            if arrow_name:
                chunks.append({
                    "file_path": file_path,
                    "start_line": node.start_point[0] + 1,
                    "end_line": node.end_point[0] + 1,
                    "language": "JavaScript",
                    "chunk_type": "function",
                    "function_name": arrow_name,
                    "parent_class": parent_class,
                    "source_code": extract_node_text(node, source_bytes)
                })
        else:
            for child in node.children:
                traverse(child, parent_class)

    traverse(root_node)
    return chunks

def extract_typescript_chunks(root_node: Node, source_bytes: bytes, file_path: str) -> List[Dict[str, Any]]:
    """Extract chunks from a TypeScript syntax tree."""
    chunks = []
    
    def get_arrow_func_name(node: Node) -> Optional[str]:
        if node.parent and node.parent.type == "variable_declarator":
            name_node = node.parent.child_by_field_name("name")
            if name_node:
                return extract_node_text(name_node, source_bytes)
        if node.parent and node.parent.type == "assignment_expression":
            left_node = node.parent.child_by_field_name("left")
            if left_node:
                return extract_node_text(left_node, source_bytes)
        return None

    def traverse(node: Node, parent_class: Optional[str] = None):
        if node.type in ("class_declaration", "interface_declaration"):
            class_name_node = node.child_by_field_name("name")
            class_name = extract_node_text(class_name_node, source_bytes) if class_name_node else None
            chunks.append({
                "file_path": file_path,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "language": "TypeScript",
                "chunk_type": "class",
                "function_name": None,
                "parent_class": parent_class,
                "source_code": extract_node_text(node, source_bytes)
            })
            
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    traverse(child, class_name)
                    
        elif node.type == "method_definition":
            method_name_node = node.child_by_field_name("name")
            method_name = extract_node_text(method_name_node, source_bytes) if method_name_node else None
            chunks.append({
                "file_path": file_path,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "language": "TypeScript",
                "chunk_type": "function",
                "function_name": method_name,
                "parent_class": parent_class,
                "source_code": extract_node_text(node, source_bytes)
            })
            
        elif node.type == "function_declaration":
            func_name_node = node.child_by_field_name("name")
            func_name = extract_node_text(func_name_node, source_bytes) if func_name_node else None
            chunks.append({
                "file_path": file_path,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "language": "TypeScript",
                "chunk_type": "function",
                "function_name": func_name,
                "parent_class": parent_class,
                "source_code": extract_node_text(node, source_bytes)
            })
            
        elif node.type == "arrow_function":
            arrow_name = get_arrow_func_name(node)
            if arrow_name:
                chunks.append({
                    "file_path": file_path,
                    "start_line": node.start_point[0] + 1,
                    "end_line": node.end_point[0] + 1,
                    "language": "TypeScript",
                    "chunk_type": "function",
                    "function_name": arrow_name,
                    "parent_class": parent_class,
                    "source_code": extract_node_text(node, source_bytes)
                })
        else:
            for child in node.children:
                traverse(child, parent_class)

    traverse(root_node)
    return chunks

def extract_java_chunks(root_node: Node, source_bytes: bytes, file_path: str) -> List[Dict[str, Any]]:
    """Extract chunks from a Java syntax tree."""
    chunks = []

    def traverse(node: Node, parent_class: Optional[str] = None):
        if node.type in ("class_declaration", "interface_declaration"):
            class_name_node = node.child_by_field_name("name")
            class_name = extract_node_text(class_name_node, source_bytes) if class_name_node else None
            chunks.append({
                "file_path": file_path,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "language": "Java",
                "chunk_type": "class",
                "function_name": None,
                "parent_class": parent_class,
                "source_code": extract_node_text(node, source_bytes)
            })
            
            body = node.child_by_field_name("body")
            if body:
                for child in body.children:
                    traverse(child, class_name)
                    
        elif node.type == "method_declaration":
            method_name_node = node.child_by_field_name("name")
            method_name = extract_node_text(method_name_node, source_bytes) if method_name_node else None
            chunks.append({
                "file_path": file_path,
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "language": "Java",
                "chunk_type": "function",
                "function_name": method_name,
                "parent_class": parent_class,
                "source_code": extract_node_text(node, source_bytes)
            })
            
        else:
            for child in node.children:
                traverse(child, parent_class)

    traverse(root_node)
    return chunks


def chunk_repo(file_path: str, language: str) -> List[Dict[str, Any]]:
    """
    Main entry point for AST-based chunking.
    Extracts syntactically complete units (functions, classes, docstrings) from a file.
    """
    if language not in ["Python", "JavaScript", "TypeScript", "Java"]:
        raise UnsupportedLanguageError(f"AST chunking not supported for {language}")
        
    try:
        with open(file_path, "rb") as f:
            source_bytes = f.read()
    except OSError:
        return []

    if not source_bytes:
        return []

    parser = get_parser(language)
    if not parser:
        return []
        
    tree = parser.parse(source_bytes)
    root_node = tree.root_node
    
    if language == "Python":
        return extract_python_chunks(root_node, source_bytes, file_path)
    elif language == "JavaScript":
        return extract_javascript_chunks(root_node, source_bytes, file_path)
    elif language == "TypeScript":
        return extract_typescript_chunks(root_node, source_bytes, file_path)
    elif language == "Java":
        return extract_java_chunks(root_node, source_bytes, file_path)
        
    return []
