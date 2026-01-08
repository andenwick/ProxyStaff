#!/usr/bin/env python3
"""
Semantic Context Loader - Uses LLM-based understanding instead of keyword matching.

This replaces the brittle keyword-based matching with actual semantic understanding.
The LLM reads pattern descriptions and determines which pattern best matches the task.

Input JSON:
{
    "task": "Description of what you're trying to do",
    "explicit_workflows": ["workflow_name"],  // Optional: force load specific workflows
    "include_memory": true  // Default: true
}

Output JSON:
{
    "status": "success",
    "matched_pattern": "outbound_campaign",
    "confidence": 0.95,
    "reasoning": "The task involves sending emails to prospects as part of a campaign...",
    "context": {
        "workflows": ["outbound_email", "campaigns"],
        "workflow_content": {...},
        "memory": {...},
        "tools": [...],
        "related_files": [...]
    },
    "recommendations": [...]
}
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess


def load_context_map() -> Dict:
    """Load the context_map.json file."""
    context_map_path = Path("operations/context_map.json")

    if not context_map_path.exists():
        return {
            "task_patterns": {},
            "workflow_dependencies": {}
        }

    with open(context_map_path, 'r') as f:
        return json.load(f)


def semantic_pattern_match(task: str, context_map: Dict) -> Optional[tuple]:
    """
    Use Claude to semantically match task to pattern.
    Returns (pattern_key, confidence, reasoning) or None.
    """
    # Build pattern descriptions for Claude
    patterns_desc = []
    for pattern_key, pattern_data in context_map.get("task_patterns", {}).items():
        desc = f"""
Pattern: {pattern_key}
Description: {pattern_data.get('description', 'No description')}
Workflows: {', '.join(pattern_data.get('workflows', []))}
Tools: {', '.join(pattern_data.get('tools', [])[:5])}{'...' if len(pattern_data.get('tools', [])) > 5 else ''}
"""
        patterns_desc.append(desc.strip())

    prompt = f"""Analyze this user task and determine which pattern best matches it.

User task: "{task}"

Available patterns:
{chr(10).join(patterns_desc)}

Respond with ONLY valid JSON (no markdown, no explanation):
{{
  "matched_pattern": "pattern_key or null if no good match",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation of why this pattern matches"
}}

If no pattern is a good match (confidence < 0.3), return null for matched_pattern.
"""

    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        message = client.messages.create(
            model="claude-3-haiku-20240307",  # Fast, cheap for this task
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text
        result = json.loads(response_text)

        matched = result.get("matched_pattern")
        if matched:
            return (
                matched,
                result.get("confidence", 0.5),
                result.get("reasoning", "")
            )
        return None

    except Exception as e:
        raise RuntimeError(f"Failed to perform semantic pattern matching: {str(e)}. Ensure ANTHROPIC_API_KEY is set.")


def load_workflow_file(workflow_name: str) -> Optional[str]:
    """Load a workflow markdown file content."""
    workflow_path = Path(f"operations/workflows/{workflow_name}.md")

    if not workflow_path.exists():
        return None

    with open(workflow_path, 'r') as f:
        return f.read()


def load_memory_data(memory_keys: List[str]) -> Dict:
    """Load memory data using the recall.py tool."""
    memory_data = {}

    for key in memory_keys:
        # Handle nested keys like "identity.email"
        if "." in key:
            file_key = key.split(".")[0]
        else:
            file_key = key

        try:
            result = subprocess.run(
                [sys.executable, "shared_tools/recall.py"],
                input=json.dumps({"file": file_key}),
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data.get("status") == "success":
                    memory_data[file_key] = data.get("data", {})
        except Exception:
            pass

    return memory_data


def get_related_workflows(workflow: str, context_map: Dict) -> List[str]:
    """Get related workflows based on dependencies."""
    deps = context_map.get("workflow_dependencies", {}).get(workflow, {})
    return deps.get("related", [])


def generate_recommendations(
    pattern_key: str,
    context_data: Dict,
    context_map: Dict
) -> List[str]:
    """Generate helpful recommendations based on loaded context."""
    recommendations = []

    # Check for pending approvals if this is a campaign task
    if pattern_key in ["outbound_campaign", "reply_processing"]:
        try:
            result = subprocess.run(
                ["python", "shared_tools/list_pending_actions.py"],
                input="{}",
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                pending = len(data.get("actions", []))
                if pending > 0:
                    recommendations.append(f"Found {pending} pending action(s) awaiting approval")
        except:
            pass

    # Suggest related workflows
    workflows = context_data.get("workflows", [])
    for workflow in workflows:
        related = get_related_workflows(workflow, context_map)
        for rel in related:
            if rel not in workflows:
                recommendations.append(f"Consider also loading '{rel}' workflow")

    return recommendations


def main():
    try:
        input_data = json.loads(sys.stdin.read())

        task = input_data.get("task", "")
        explicit_workflows = input_data.get("explicit_workflows", [])
        include_memory = input_data.get("include_memory", True)

        if not task and not explicit_workflows:
            raise ValueError("Must provide either 'task' or 'explicit_workflows'")

        # Load context map
        context_map = load_context_map()

        # Semantically match task to pattern
        matched_pattern = None
        confidence = 0.0
        reasoning = ""
        pattern_data = {}

        if task:
            match_result = semantic_pattern_match(task, context_map)
            if match_result:
                matched_pattern, confidence, reasoning = match_result
                pattern_data = context_map["task_patterns"].get(matched_pattern, {})

        # Gather workflows
        workflows_to_load = list(explicit_workflows)
        if pattern_data:
            workflows_to_load.extend(pattern_data.get("workflows", []))

        # Remove duplicates while preserving order
        workflows_to_load = list(dict.fromkeys(workflows_to_load))

        # Load workflow content
        workflow_content = {}
        for workflow in workflows_to_load:
            content = load_workflow_file(workflow)
            if content:
                workflow_content[workflow] = content

        # Load memory
        memory_data = {}
        if include_memory and pattern_data:
            memory_keys = pattern_data.get("memory", [])
            memory_data = load_memory_data(memory_keys)

        # Build context response
        context = {
            "workflows": workflows_to_load,
            "workflow_content": workflow_content,
            "memory": memory_data,
            "tools": pattern_data.get("tools", []),
            "related_files": pattern_data.get("related_files", [])
        }

        # Generate recommendations
        recommendations = generate_recommendations(
            matched_pattern or "unknown",
            context,
            context_map
        )

        result = {
            "status": "success",
            "matched_pattern": matched_pattern,
            "confidence": round(confidence, 2) if confidence else 0,
            "reasoning": reasoning,
            "context": context,
            "recommendations": recommendations
        }

        print(json.dumps(result, indent=2))

    except Exception as e:
        error_result = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(error_result))
        sys.exit(1)


if __name__ == "__main__":
    main()
