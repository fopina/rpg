#!/usr/bin/env python3
"""Import a Microsoft To Do JSON export into an existing Notion database."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request

VERSION = '2025-09-03'


def rich_text(text):
    return [{'type': 'text', 'text': {'content': text[i:i + 1500]}}
            for i in range(0, len(text), 1500)]


def comments(task):
    # Keep original representations (including HTML bodies) without losing fields.
    text = json.dumps({k: v for k, v in task.items() if k != 'Subject'},
                      ensure_ascii=False, indent=2, sort_keys=True)
    parts = [text[i:i + 24000] for i in range(0, len(text), 24000)]
    return [rich_text(f'Microsoft To Do metadata ({i + 1}/{len(parts)})\n{part}')
            for i, part in enumerate(parts)]


def due_date(task):
    # To Do due dates are calendar dates, not scheduled appointment times.
    value = task.get('DueDateTime') or task.get('DueDate')
    if isinstance(value, dict):
        value = value.get('DateTime')
    return str(value)[:10] if value else None


class Notion:
    def __init__(self, token):
        self.token = token
        self.last_request = 0

    def request(self, method, path, body=None):
        encoded = json.dumps(body).encode() if body is not None else None
        for attempt in range(6):
            time.sleep(max(0, 0.4 - (time.monotonic() - self.last_request)))
            req = urllib.request.Request('https://api.notion.com/v1' + path,
                data=encoded, method=method, headers={
                    'Authorization': 'Bearer ' + self.token,
                    'Notion-Version': VERSION, 'Content-Type': 'application/json'})
            self.last_request = time.monotonic()
            try:
                with urllib.request.urlopen(req, timeout=60) as response:
                    return json.load(response)
            except urllib.error.HTTPError as exc:
                if exc.code == 429 and attempt < 5:
                    time.sleep(float(exc.headers.get('Retry-After', '2')))
                    continue
                # POST failures may have committed: never blindly retry writes.
                raise RuntimeError(f'Notion HTTP {exc.code}: {exc.read().decode()}') from exc
        raise RuntimeError('Rate-limit retries exhausted')


def status_names(schema, args):
    prop = schema['Status']
    kind = prop['type']
    if kind not in ('status', 'select'):
        raise ValueError('Status must be a status or select property')
    options = prop[kind]['options']
    names = {o['name'] for o in options}
    if kind == 'status':
        groups = prop['status'].get('groups', [])
        def from_group(name):
            ids = next((g['option_ids'] for g in groups if g['name'] == name), [])
            return next((o['name'] for o in options if o['id'] in ids), None)
        todo = args.todo_status or from_group('To-do')
        done = args.done_status or from_group('Complete')
    else:
        todo, done = args.todo_status, args.done_status
    if todo not in names or done not in names or todo == done:
        raise ValueError('Provide distinct --todo-status and --done-status matching database options. '
                         f'Available options: {sorted(names)}')
    return kind, todo, done


def properties(task, list_name, schema, status):
    title = str(task.get('Subject') or 'Untitled task')
    if len(title) > 150000:
        raise ValueError('Task title exceeds Notion rich-text array limits')
    result = {'Name': {'title': rich_text(title)}}
    kind = schema['List']['type']
    if kind == 'rich_text':
        result['List'] = {'rich_text': rich_text(list_name)}
    elif kind in ('select', 'multi_select'):
        if len(list_name) > 100 or ',' in list_name:
            raise ValueError('Use a text List property for list names with commas or over 100 characters')
        result['List'] = {kind: {'name': list_name} if kind == 'select' else [{'name': list_name}]}
    else:
        raise ValueError('List must be text, select, or multi-select')
    date = due_date(task)
    result['Due date'] = {'date': {'start': date} if date else None}
    kind, todo, done = status
    result['Status'] = {kind: {'name': done if task.get('Status') == 'Completed' else todo}}
    return result


def save_state(path, state):
    tmp = path.with_name(path.name + '.tmp')
    with tmp.open('w', encoding='utf-8') as stream:
        os.chmod(tmp, 0o600)
        json.dump(state, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    tmp.replace(path)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('export', type=Path)
    target = p.add_mutually_exclusive_group()
    target.add_argument('--database-id')
    target.add_argument('--data-source-id')
    p.add_argument('--todo-status', default='Not done', help='Unfinished option (default: Not done)')
    p.add_argument('--done-status', default='Done', help='Completed option (default: Done)')
    p.add_argument('--apply', action='store_true', help='Create pages and comments; otherwise preview only')
    p.add_argument('--state', type=Path, help='Resume journal; defaults beside the input JSON')
    args = p.parse_args()
    raw = args.export.read_bytes()
    data = json.loads(raw)
    folders = {f['Id']: f['Name'] for f in data['folders']}
    tasks = data['tasks']
    if len({t['Id'] for t in tasks}) != len(tasks):
        raise ValueError('Duplicate task IDs in input')
    for task in tasks:
        if task['ParentFolderId'] not in folders:
            raise ValueError('Task refers to an unknown list')
        if task.get('Status') not in ('Completed', 'NotStarted'):
            raise ValueError('Unsupported task status: ' + str(task.get('Status')))
    print(f'{len(folders)} lists; {len(tasks)} tasks; '
          f'{sum(t["Status"] == "Completed" for t in tasks)} completed; '
          f'{sum(bool(due_date(t)) for t in tasks)} with due dates')
    if not args.database_id and not args.data_source_id:
        if args.apply:
            p.error('--apply requires --database-id or --data-source-id')
        print('Offline preview passed. Supply a target ID to validate its schema.')
        return
    token = os.getenv('NOTION_TOKEN')
    if not token:
        p.error('Set NOTION_TOKEN in the environment')
    api = Notion(token)
    ds_id = args.data_source_id
    if not ds_id:
        sources = api.request('GET', '/databases/' + args.database_id)['data_sources']
        if len(sources) != 1:
            raise ValueError('Database has multiple data sources; specify --data-source-id')
        ds_id = sources[0]['id']
    schema = api.request('GET', '/data_sources/' + ds_id)['properties']
    for name, kind in [('Name', 'title'), ('Due date', 'date')]:
        if schema.get(name, {}).get('type') != kind:
            raise ValueError(f'{name} must be a {kind} property')
    if 'List' not in schema or 'Status' not in schema:
        raise ValueError('Database needs List and Status properties')
    status = status_names(schema, args)
    # Validate every payload before the first write.
    plans = [(t, properties(t, folders[t['ParentFolderId']], schema, status), comments(t))
             for t in tasks]
    print(f'Schema verified; Status: {status[1]!r} / {status[2]!r}; List: {schema["List"]["type"]}')
    if not args.apply:
        print('Preview only. Add --apply to import.')
        return
    state_path = args.state or args.export.with_suffix('.notion-state.json')
    signature = hashlib.sha256(json.dumps({'export': hashlib.sha256(raw).hexdigest(),
        'target': ds_id, 'status': status, 'list_type': schema['List']['type']},
        sort_keys=True).encode()).hexdigest()
    state = json.loads(state_path.read_text()) if state_path.exists() else {
        'signature': signature, 'data_source_id': ds_id, 'tasks': {}}
    if state['signature'] != signature:
        raise ValueError('Resume journal belongs to a different input, target, or mapping')
    for index, (task, props, notes) in enumerate(plans, 1):
        entry = state['tasks'].setdefault(task['Id'], {'comments_written': 0})
        if entry.get('pending'):
            raise RuntimeError(f'Uncertain previous write for task {task["Id"]}. '
                               f'Inspect Notion and reconcile {state_path} before retrying.')
        if not entry.get('page_id'):
            entry['pending'] = 'create_page'
            save_state(state_path, state)
            page = api.request('POST', '/pages', {'parent': {'type': 'data_source_id',
                'data_source_id': ds_id}, 'properties': props})
            entry['page_id'] = page['id']
            entry.pop('pending')
            save_state(state_path, state)
        for i in range(entry['comments_written'], len(notes)):
            entry['pending'] = f'comment_{i}'
            save_state(state_path, state)
            api.request('POST', '/comments', {'parent': {'page_id': entry['page_id']},
                                             'rich_text': notes[i]})
            entry['comments_written'] = i + 1
            entry.pop('pending')
            save_state(state_path, state)
        print(f'Imported {index}/{len(plans)}', flush=True)
    print(f'Import complete. Resume journal: {state_path}')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, OSError, KeyError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)
