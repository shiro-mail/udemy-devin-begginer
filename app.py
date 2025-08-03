from flask import Flask, render_template, request, redirect, jsonify
import json
import os
import uuid
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'data.json'

def load_tasks():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
                if isinstance(tasks, list) and len(tasks) > 0:
                    if isinstance(tasks[0], str) or (isinstance(tasks[0], dict) and 'id' not in tasks[0]):
                        migrated_tasks = []
                        for i, task in enumerate(tasks):
                            if isinstance(task, str):
                                migrated_tasks.append({
                                    'id': str(uuid.uuid4()),
                                    'title': task,
                                    'completed': False,
                                    'created_at': datetime.now().isoformat()
                                })
                            elif isinstance(task, dict) and 'title' in task:
                                migrated_tasks.append({
                                    'id': str(uuid.uuid4()),
                                    'title': task['title'],
                                    'completed': task.get('completed', False),
                                    'created_at': datetime.now().isoformat()
                                })
                        save_tasks(migrated_tasks)
                        return migrated_tasks
                return tasks
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_tasks(tasks):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except IOError:
        pass

@app.route('/')
def index():
    tasks = load_tasks()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add():
    task_title = request.form.get('title', '').strip()
    if task_title:
        tasks = load_tasks()
        new_task = {
            'id': str(uuid.uuid4()),
            'title': task_title,
            'completed': False,
            'created_at': datetime.now().isoformat()
        }
        tasks.append(new_task)
        save_tasks(tasks)
    return redirect('/')

@app.route('/delete/<task_id>', methods=['POST'])
def delete(task_id):
    tasks = load_tasks()
    tasks = [task for task in tasks if task.get('id') != task_id]
    save_tasks(tasks)
    return redirect('/')

@app.route('/toggle/<task_id>', methods=['POST'])
def toggle(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task.get('id') == task_id:
            task['completed'] = not task.get('completed', False)
            break
    save_tasks(tasks)
    return redirect('/')

@app.route('/edit/<task_id>', methods=['POST'])
def edit(task_id):
    new_title = request.form.get('title', '').strip()
    if new_title:
        tasks = load_tasks()
        for task in tasks:
            if task.get('id') == task_id:
                task['title'] = new_title
                break
        save_tasks(tasks)
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
