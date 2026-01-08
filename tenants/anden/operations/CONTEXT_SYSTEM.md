# Context System Documentation

## Overview

The context system solves two key problems:
1. **Context Fragmentation** - AI loads directives on-demand and might miss connections
2. **Tool Manifest Verbosity** - 1,279 lines of JSON is hard to maintain

## Components

### 1. Context Map (`operations/context_map.json`)

Maps tasks to required context (workflows, memory, tools). The AI uses this to auto-load relevant resources before starting work.

**Structure:**
```json
{
  "task_patterns": {
    "pattern_name": {
      "triggers": ["keywords", "that", "match"],
      "workflows": ["workflow1", "workflow2"],
      "memory": ["identity", "business"],
      "tools": ["tool1", "tool2"],
      "related_files": ["path/to/file"]
    }
  },
  "workflow_dependencies": {
    "workflow_name": {
      "requires": ["required/file.md"],
      "related": ["related_workflow"]
    }
  }
}
```

**Current Patterns:**
- `outbound_campaign` - Process sales campaigns
- `email_operations` - Send/read emails
- `calendar_booking` - Schedule meetings
- `browser_automation` - Automate web tasks
- `crypto_management` - Handle crypto
- `google_drive_operations` - Work with Drive
- `prospect_research` - Research prospects
- `reply_processing` - Process campaign replies
- `daily_routines` - Scheduled tasks

### 2. Split Tool Manifests (`execution/tools/*.json`)

Tools are organized by category for easier maintenance:

```
execution/tools/
├── email_tools.json       # Gmail, SendGrid
├── browser_tools.json     # Browser automation
├── drive_tools.json       # Google Drive/Docs
├── calendar_tools.json    # Calendar operations
├── crypto_tools.json      # Coinbase operations
├── prospecting_tools.json # Prospect research
└── utility_tools.json     # Testing and utilities
```

**Tool count by category:**
- Browser: 9 tools
- Google Drive: 12 tools
- Email: 4 tools
- Calendar: 2 tools
- Crypto: 4 tools
- Prospecting: 3 tools
- Utility: 3 tools

### 3. Context Loader (`shared_tools/load_context.py`)

Intelligently loads required context for a task.

**Usage:**
```bash
echo '{"task": "I need to send outbound campaign emails"}' | python shared_tools/load_context.py
```

**Output:**
```json
{
  "status": "success",
  "matched_pattern": "outbound_campaign",
  "confidence": 0.95,
  "context": {
    "workflows": ["outbound_email", "campaigns"],
    "workflow_content": {"outbound_email": "..."},
    "memory": {"identity": {...}, "business": {...}},
    "tools": ["research_website", "gmail_send", ...],
    "related_files": ["operations/campaigns/proxystaff-outbound/"]
  },
  "recommendations": [
    "Found 5 pending action(s) awaiting approval"
  ]
}
```

**Features:**
- Pattern matching with confidence scores
- Automatic workflow loading
- Memory retrieval
- Contextual recommendations
- Related file suggestions

### 4. Manifest Merger (`shared_tools/merge_tool_manifests.py`)

Combines split manifests into a single file for the MCP server.

**Usage:**
```bash
python shared_tools/merge_tool_manifests.py
```

Creates `execution/tool_manifest_merged.json` with all tools.

## How to Use

### For the AI Assistant

**Before starting a task, load context:**
```bash
echo '{"task": "send campaign emails to prospects"}' | python shared_tools/load_context.py
```

This returns everything you need:
- Which workflows to read
- What memory to load
- Which tools are relevant
- Any recommendations

**Example workflow:**
```
1. User: "Process the ProxyStaff campaign"
2. AI calls load_context with task description
3. AI receives:
   - Load workflows: outbound_email, campaigns
   - Load memory: identity, business
   - Tools: research_website, gmail_send, campaign_read
   - Recommendation: "5 pending approvals"
4. AI reads loaded workflows and proceeds with full context
```

### For Developers

**Adding a new task pattern:**

Edit `operations/context_map.json`:
```json
{
  "task_patterns": {
    "your_new_pattern": {
      "description": "What this pattern is for",
      "triggers": ["keywords", "that", "indicate", "this task"],
      "workflows": ["workflow_files_to_load"],
      "memory": ["memory_keys_needed"],
      "tools": ["relevant_tools"],
      "related_files": ["paths/to/important/files"]
    }
  }
}
```

**Adding a new tool category:**

1. Create `execution/tools/your_category_tools.json`:
```json
{
  "category": "your_category",
  "description": "What these tools do",
  "tools": [
    {
      "name": "tool_name",
      "description": "Tool description",
      "script": "tool_script.py",
      "input_schema": {...}
    }
  ]
}
```

2. Run merger:
```bash
python shared_tools/merge_tool_manifests.py
```

**Adding workflow dependencies:**

Edit `operations/context_map.json`:
```json
{
  "workflow_dependencies": {
    "your_workflow": {
      "requires": ["identity/profile.md"],
      "related": ["another_workflow"]
    }
  }
}
```

## Benefits

### Before Context System

**Problems:**
- AI loads directives randomly, might miss related workflows
- 1,279 line tool_manifest.json is hard to scan and edit
- No automatic suggestions or recommendations
- Memory loaded manually each time

**Example issue:**
```
User: "Process campaign"
AI: Loads campaigns.md only
AI: Doesn't realize it needs outbound_email.md
AI: Misses that there are 5 pending approvals
Result: Incomplete context, poor decisions
```

### After Context System

**Improvements:**
- Pattern matching auto-loads related workflows
- Tools split into 7 manageable categories
- Contextual recommendations provided automatically
- Memory loaded automatically based on task

**Same example:**
```
User: "Process campaign"
AI: Calls load_context("process campaign")
AI: Gets outbound_email + campaigns workflows
AI: Gets identity + business memory
AI: Sees recommendation: "5 pending approvals"
Result: Full context, good decisions
```

## Maintenance

### Keep Context Map Updated

When adding new workflows or changing relationships, update `context_map.json`.

**Check for orphaned patterns:**
```bash
# List all workflows
ls operations/workflows/*.md | xargs -n1 basename | sed 's/.md//'

# Compare to context_map.json to find missing patterns
```

### Merge Tool Manifests After Changes

After editing any `execution/tools/*.json` file:
```bash
python shared_tools/merge_tool_manifests.py
```

This updates `tool_manifest_merged.json` which the MCP server reads.

### Test Pattern Matching

Test if your triggers work:
```bash
echo '{"task": "your test task description"}' | python shared_tools/load_context.py
```

Check:
- Does it match the right pattern?
- Is confidence > 0.5?
- Are the right workflows loaded?

## Migration Notes

**Original tool_manifest.json:**
- Kept for reference
- Not used by MCP server anymore
- Can be deleted once migration is verified

**New merged manifest:**
- Generated from split files
- Used by MCP server
- Regenerate after any tool changes

## Future Improvements

**Possible enhancements:**
1. **Fuzzy matching** - Use embeddings for better pattern matching
2. **Usage tracking** - Learn which workflows are actually used together
3. **Auto-updating** - Detect new workflows and suggest pattern additions
4. **Validation** - Check that referenced workflows and tools exist

## Troubleshooting

**Context loader returns no match:**
- Check if your task description contains any trigger words
- Add more triggers to the pattern
- Test with `echo '{"task": "..."}' | python shared_tools/load_context.py`

**Tools missing after merge:**
- Verify the tool exists in a category manifest
- Check JSON syntax in the category file
- Re-run `merge_tool_manifests.py`

**Recommendations not appearing:**
- Check if the pattern has specific recommendation logic
- Edit `load_context.py` to add pattern-specific checks

**Memory not loading:**
- Verify `recall.py` works: `echo '{"file": "identity"}' | python shared_tools/recall.py`
- Check memory keys in pattern match the actual memory files
