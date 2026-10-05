---
title: "0x308D Moving the To-Do List"
date: 2026-10-05T12:00:00+01:00
draft: true
toc: false
tags:
  - productivity
  - tasks
  - notion
  - obsidian
---

<!-- TODO before publishing: include the migration scripts and explain how to run them,
what data they transfer, and any limitations.

Existing migration/export scripts: https://github.com/fopina/trello-to-mstodo
- import_from_trello.py covers the Trello -> Microsoft To Do migration.
- export_all.py exports To Do folders and task objects; the README currently calls
  it export.py. Use --completed --output BACKUP.json to include completed tasks.
- Verified against captured browser requests: client.py uses the same
  https://substrate.office.com/todob2/api/v1 taskfolders and per-folder tasks API.
  Task ParentFolderId maps to folder Id; folder Name is preserved in the export.
- Before relying on a complete export, implement pagination for folders and tasks.
  The client requests 200 items and raises at >=200, but does not follow DeltaLink.
  Browser verification returned task pages of 50, 19, then 0 by following DeltaLink.
- Compare linked-entity coverage: the browser adds $expand=LinkedEntity; the client
  does not. Separately verify checklist/subtask and attachment export coverage.
-->

Keeping a to-do list should be the easy part. Doing the things on it is already enough work...

Yet here I am, moving between task managers again: Trello, then Microsoft To Do, then Notion for personal tasks and local Obsidian at work. With the iOS Synctasks app in the mix for the personal side.

The first move was about friction. The second was about hundreds of tasks disappearing.

### Trello: too much dragging

I used Trello to keep track of tasks, but dragging cards around never felt particularly quick or efficient to me. A board gives you a nice overview; maintaining that board was more interaction than I wanted for a to-do list.

When I need to capture something or update a task, I want that out of the way quickly. Moving cards around was getting in the way often enough that I wanted something simpler.

There was also a much less subjective reason to leave: Trello was not approved at work. Microsoft To Do was.

So I moved to To Do. A straightforward task list, and something I could use at work without that approval problem. Good enough!

### Microsoft To Do: nothing left to do?

Then To Do purged all my non-completed tasks. Hundreds of them.

That is certainly one way to clear a backlog...

I had no recovery option available to get them back. Whatever caused the disappearance, the result for me was the same: the tasks I was relying on the app to remember were gone.

The unfinished tasks are precisely the ones I need a task manager to keep. Some are things I need to do soon; others are there so I do not have to keep remembering them. Losing that list defeats the whole point of having it.

After that, I was done with To Do. Moving again meant rebuilding what I could, rather than neatly transferring an intact backlog to a new app.

### Notion at home, Obsidian at work

For personal use, I moved to Notion tasks, with the iOS Synctasks app as part of that setup. The phone matters here too: the original frustration with Trello was how much effort it took to interact with my tasks, so the day-to-day mobile experience belongs in the decision.

Work went a different way. Notion is not approved there, so it could not replace To Do for both sides of my life. I now use local Obsidian for work tasks.

That leaves me with two places for tasks, shaped partly by what I want to use and partly by what I can use at work. Having everything in one app was convenient, but it stopped being much of a selling point after that app lost the unfinished list.

I left Trello because updating tasks felt cumbersome and it was not approved at work. I left To Do because my tasks disappeared. Now it is Notion with Synctasks for personal use, and local Obsidian for work.

Hopefully the next thing I do with the list is actually finish something on it.
