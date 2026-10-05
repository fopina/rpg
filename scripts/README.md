# Microsoft To Do → Notion

`todo_to_notion.py` reads the exported `{ "folders": [...], "tasks": [...] }` JSON
and creates one page per task in an existing Notion database. Python 3 is the only
dependency.

| Export field | Notion property |
| --- | --- |
| `Subject` | `Name` (title) |
| Folder `Name`, resolved via `ParentFolderId` | `List` (text, select, or multi-select) |
| `DueDateTime.DateTime`, with `DueDate` fallback | `Due date` (date) |
| `Status: NotStarted` | `Status: Not done` |
| `Status: Completed` | `Status: Done` |

`Missed` is never assigned. Due dates are imported as calendar dates; tasks without
one get an empty date property. The remaining original task fields are preserved
in page comments as JSON, including HTML descriptions, recurrence and any nested
subtask data present in the export. Long metadata is split across comments without
truncation. This does not fetch missing subtasks or attachment files from To Do.

## Setup and usage

Use a Notion connection with read/insert content and insert comments capabilities,
and grant it access to the target database. Set its secret as `NOTION_TOKEN` in your
environment. The script never writes that secret into its progress file.

Configure SyncTasks to use this database and map its task title, date, and completion
fields to `Name`, `Due date`, and `Status` (`Done` means completed). Use `List` when
configuring list filters. SyncTasks compatibility still needs an in-app check;
page comments are preserved in Notion, but their display in SyncTasks is unverified.

First validate the input locally (no token or network required):

```sh
python3 scripts/todo_to_notion.py "$HOME/microsoft-todo-export-2026-10-05.json"
```

Validate the destination schema without creating pages:

```sh
python3 scripts/todo_to_notion.py "$HOME/microsoft-todo-export-2026-10-05.json" \
  --database-id DATABASE_ID
```

Import after the preview succeeds:

```sh
python3 scripts/todo_to_notion.py "$HOME/microsoft-todo-export-2026-10-05.json" \
  --database-id DATABASE_ID --apply
```

If the database contains multiple data sources, use `--data-source-id` instead.
The script uses Notion API version `2025-09-03`. It validates all property payloads
before creating the first page, spaces requests, and honors rate-limit responses.
Select/multi-select list options may be added by Notion when pages are created.

## Resuming

The progress file defaults to `microsoft-todo-export-2026-10-05.notion-state.json`
beside the export, outside the repository. Rerun the same command with the same
input, destination, mapping, and progress file to skip finished pages and comments.
Keep this file: a fresh journal creates a fresh set of pages, and the importer does
not deduplicate against pages created by other tools or previous journals.

Before each write, the script records a `pending` operation. If a request fails or
the process stops before recording its response, it stops on the next run rather
than risk duplicating a page or comment. Reconcile that entry manually:

- For `create_page`, find the page in Notion and record its `page_id`, then remove
  `pending`. If the page was definitely not created, just remove `pending`.
- For `comment_N`, check whether that numbered metadata comment exists. If it does,
  set `comments_written` to `N + 1`; otherwise leave the count unchanged. Remove
  `pending` after checking.

Do not run two imports concurrently with the same progress file. Successful
imports do not modify or delete the original To Do tasks.

API references: [Create page](https://developers.notion.com/reference/post-page),
[Create comment](https://developers.notion.com/reference/create-a-comment),
[Data sources](https://developers.notion.com/reference/retrieve-a-data-source),
[Request limits](https://developers.notion.com/reference/request-limits).
