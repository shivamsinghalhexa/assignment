import os
import json
import datetime
import re
import sys
try:
    import speech_recognition as sr
except ImportError:
    sr = None  # Speech recognition is optional for testing

TASKS_FILE = 'tasks.json'
PRIORITIES = ['low', 'medium', 'high']


def parse_natural_date(text):
    today = datetime.date.today()
    text = text.lower().strip()
    if text == 'today':
        return today
    elif text == 'tomorrow':
        return today + datetime.timedelta(days=1)
    elif text == 'day after tomorrow':
        return today + datetime.timedelta(days=2)
    elif text == 'yesterday':
        return today - datetime.timedelta(days=1)
    else:
        # Try to parse as YYYY-MM-DD
        try:
            return datetime.datetime.strptime(text, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError(f"Invalid date: {text}")


class TaskManager:
    def __init__(self, filename=TASKS_FILE):
        self.filename = filename
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.tasks = json.load(f)
            except Exception as e:
                print(f"Error loading tasks: {e}")
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.tasks, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def add_task(self, description, priority='medium', due_date=None):
        if priority not in PRIORITIES:
            raise ValueError(f"Invalid priority: {priority}")
        task = {
            'description': description,
            'priority': priority,
            'due_date': due_date.isoformat() if due_date else None,
            'completed': False
        }
        self.tasks.append(task)
        self.save_tasks()
        print(f"Task added: {description} (Priority: {priority}, Due: {due_date})")

    def list_tasks(self):
        if not self.tasks:
            print("No tasks found.")
            return
        for idx, task in enumerate(self.tasks, 1):
            status = '✓' if task['completed'] else '✗'
            due = task['due_date'] if task['due_date'] else 'No due date'
            print(f"{idx}. [{status}] {task['description']} (Priority: {task['priority']}, Due: {due})")

    def complete_task(self, index):
        if index < 1 or index > len(self.tasks):
            print(f"Invalid task number: {index}")
            return
        self.tasks[index - 1]['completed'] = True
        self.save_tasks()
        print(f"Task {index} marked as completed.")

    def process_command(self, command):
        command = command.lower().strip()
        if command.startswith('add '):
            # Example: add submit report with high priority due tomorrow
            m = re.match(r'add (.+?)(?: with (low|medium|high) priority)?(?: due (.+))?$', command)
            if not m:
                print("Could not parse add command. Try: 'add <task> with <priority> priority due <date>'")
                return
            desc = m.group(1)
            priority = m.group(2) if m.group(2) else 'medium'
            due_str = m.group(3)
            due_date = None
            if due_str:
                try:
                    due_date = parse_natural_date(due_str)
                except Exception as e:
                    print(f"Error parsing date: {e}")
                    return
            try:
                self.add_task(desc, priority, due_date)
            except Exception as e:
                print(f"Error adding task: {e}")
        elif command.startswith('list'):
            self.list_tasks()
        elif command.startswith('complete '):
            # Example: complete 2
            m = re.match(r'complete (\d+)', command)
            if not m:
                print("Could not parse complete command. Try: 'complete <task number>'")
                return
            idx = int(m.group(1))
            self.complete_task(idx)
        else:
            print("Unknown command. Try: add, list, or complete.")


def recognize_voice():
    if sr is None:
        print("speech_recognition not installed. Please type your command.")
        return input('> ')
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say your command...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return ''
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return ''


def main():
    tm = TaskManager()
    print("Voice Task Manager CLI")
    print("Commands: add <task> with <priority> priority due <date>, list, complete <number>, or 'exit'")
    while True:
        if sr is not None:
            print("Speak or type your command (or 'exit'):")
        else:
            print("Type your command (or 'exit'):")
        try:
            command = recognize_voice() if sr is not None else input('> ')
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        if not command:
            continue
        if command.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        tm.process_command(command)


if __name__ == '__main__':
    main() 