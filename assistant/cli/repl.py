from __future__ import annotations
import os
import shlex
import sys
from difflib import get_close_matches
from typing import Dict, List, Optional

from assistant.services.contacts_service import ContactsService
from assistant.services.notes_service import NotesService
from assistant.storage.json_store import JSONStorage


DATA_DIR = os.path.join(os.path.expanduser("~"), ".assistant")
CONTACTS_FILE = os.path.join(DATA_DIR, "contacts.json")
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")


def print_line(text: str = "") -> None:
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


def format_contact(c: Dict) -> str:
    parts: List[str] = [
        f"id={c.get('id')}",
        f"name={c.get('name')}",
    ]
    if c.get("address"):
        parts.append(f"address={c.get('address')}")
    if c.get("phones"):
        parts.append(f"phones={', '.join(c.get('phones'))}")
    if c.get("email"):
        parts.append(f"email={c.get('email')}")
    if c.get("birthday"):
        parts.append(f"birthday={c.get('birthday')}")
    if c.get("days_until_birthday") is not None:
        parts.append(f"in={c.get('days_until_birthday')}d")
    return "; ".join(parts)


def format_note(n: Dict) -> str:
    parts: List[str] = [
        f"id={n.get('id')}",
        f"text={n.get('text')}",
    ]
    if n.get("tags"):
        parts.append(f"tags={', '.join(n.get('tags'))}")
    parts.append(f"updated={n.get('updated_at')}")
    return "; ".join(parts)


HELP_TEXT = """
Commands:
  help                                   Show this help
  exit | quit                            Exit the assistant

  contact add name="..." [address="..."] [phones="+123, +456"] [email="..."] [birthday="YYYY-MM-DD"]
  contact list
  contact search <query>
  contact edit <id> [name="..."] [address="..."] [phones="+123, +456"] [email="..."] [birthday="YYYY-MM-DD"]
  contact delete <id>
  contact birthdays <days>

  note add text="..." [tags="tag1,tag2"]
  note list [sort=created|updated|text|tags]
  note search <query>
  note search-tags <tag1,tag2>
  note edit <id> [text="..."] [tags="tag1,tag2"]
  note delete <id>
""".strip()


VALID_COMMANDS = [
    "help",
    "exit",
    "quit",
    "contact add",
    "contact list",
    "contact search",
    "contact edit",
    "contact delete",
    "contact birthdays",
    "note add",
    "note list",
    "note search",
    "note search-tags",
    "note edit",
    "note delete",
]


def suggest_command(input_line: str) -> Optional[str]:
    # Try to match against known commands by first two tokens
    tokens = shlex.split(input_line)
    if not tokens:
        return None
    head = " ".join(tokens[:2]) if len(tokens) >= 2 else tokens[0]
    matches = get_close_matches(head, VALID_COMMANDS, n=1, cutoff=0.6)
    return matches[0] if matches else None


def parse_kv(args: List[str]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for token in args:
        if "=" in token:
            key, value = token.split("=", 1)
            value = value.strip()
            if len(value) >= 2 and ((value[0] == value[-1]) and value[0] in ('"', "'")):
                value = value[1:-1]
            result[key.strip()] = value
    return result


class App:
    def __init__(self) -> None:
        self.contacts = ContactsService(JSONStorage(CONTACTS_FILE))
        self.notes = NotesService(JSONStorage(NOTES_FILE))

    def handle_line(self, line: str) -> bool:
        try:
            tokens = shlex.split(line)
        except ValueError as e:
            print_line(f"Parse error: {e}")
            return True
        if not tokens:
            return True

        cmd = tokens[0].lower()

        if cmd in ("exit", "quit"):
            return False
        if cmd == "help":
            print_line(HELP_TEXT)
            return True
        if cmd == "contact":
            return self._handle_contact(tokens[1:])
        if cmd == "note":
            return self._handle_note(tokens[1:])

        suggestion = suggest_command(line)
        print_line(f"Unknown command. {('Did you mean: ' + suggestion) if suggestion else 'Type: help'}")
        return True

    def _handle_contact(self, args: List[str]) -> bool:
        if not args:
            print_line("Missing subcommand. Try: contact list | contact add | help")
            return True
        sub = args[0].lower()
        if sub == "add":
            fields = parse_kv(args[1:])
            name = fields.get("name")
            if not name:
                print_line("name is required")
                return True
            try:
                contact = self.contacts.add_contact(
                    name=name,
                    address=fields.get("address"),
                    phones=[p.strip() for p in (fields.get("phones") or "").split(",") if p.strip()],
                    email=fields.get("email"),
                    birthday=fields.get("birthday"),
                )
                print_line("Added contact: " + format_contact(contact))
            except Exception as e:
                print_line(f"Error: {e}")
            return True
        if sub == "list":
            items = self.contacts.list_contacts()
            if not items:
                print_line("No contacts yet.")
                return True
            for c in items:
                print_line(format_contact(c))
            return True
        if sub == "search":
            if len(args) < 2:
                print_line("Usage: contact search <query>")
                return True
            query = " ".join(args[1:])
            items = self.contacts.search_contacts(query)
            if not items:
                print_line("No matches.")
                return True
            for c in items:
                print_line(format_contact(c))
            return True
        if sub == "edit":
            if len(args) < 2:
                print_line("Usage: contact edit <id> [name=..] [address=..] [phones=..] [email=..] [birthday=..]")
                return True
            contact_id = args[1]
            fields = parse_kv(args[2:])
            try:
                updated = self.contacts.edit_contact(contact_id, **fields)
                if not updated:
                    print_line("Contact not found")
                else:
                    print_line("Updated: " + format_contact(updated))
            except Exception as e:
                print_line(f"Error: {e}")
            return True
        if sub == "delete":
            if len(args) < 2:
                print_line("Usage: contact delete <id>")
                return True
            found = self.contacts.delete_contact(args[1])
            print_line("Deleted" if found else "Contact not found")
            return True
        if sub == "birthdays":
            if len(args) < 2:
                print_line("Usage: contact birthdays <days>")
                return True
            try:
                days = int(args[1])
            except ValueError:
                print_line("days must be an integer")
                return True
            items = self.contacts.birthdays_in(days)
            if not items:
                print_line("No upcoming birthdays.")
                return True
            for c in items:
                print_line(format_contact(c))
            return True
        suggestion = suggest_command("contact " + sub)
        print_line(f"Unknown contact subcommand. {('Did you mean: ' + suggestion) if suggestion else 'Type: help'}")
        return True

    def _handle_note(self, args: List[str]) -> bool:
        if not args:
            print_line("Missing subcommand. Try: note list | note add | help")
            return True
        sub = args[0].lower()
        if sub == "add":
            fields = parse_kv(args[1:])
            text = fields.get("text")
            if not text:
                print_line("text is required")
                return True
            try:
                note = self.notes.add_note(text=text, tags_text=fields.get("tags"))
                print_line("Added note: " + format_note(note))
            except Exception as e:
                print_line(f"Error: {e}")
            return True
        if sub == "list":
            sort_by = "created"
            if len(args) >= 2 and args[1].startswith("sort="):
                sort_by = args[1].split("=", 1)[1]
            items = self.notes.list_notes(sort_by=sort_by)
            if not items:
                print_line("No notes yet.")
                return True
            for n in items:
                print_line(format_note(n))
            return True
        if sub == "search":
            if len(args) < 2:
                print_line("Usage: note search <query>")
                return True
            query = " ".join(args[1:])
            items = self.notes.search_notes(query)
            if not items:
                print_line("No matches.")
                return True
            for n in items:
                print_line(format_note(n))
            return True
        if sub == "search-tags":
            if len(args) < 2:
                print_line("Usage: note search-tags <tag1,tag2>")
                return True
            tags = [t.strip() for t in args[1].split(",") if t.strip()]
            items = self.notes.search_by_tags(tags)
            if not items:
                print_line("No matches.")
                return True
            for n in items:
                print_line(format_note(n))
            return True
        if sub == "edit":
            if len(args) < 2:
                print_line("Usage: note edit <id> [text=..] [tags=..]")
                return True
            note_id = args[1]
            fields = parse_kv(args[2:])
            try:
                updated = self.notes.edit_note(note_id, **fields)
                if not updated:
                    print_line("Note not found")
                else:
                    print_line("Updated: " + format_note(updated))
            except Exception as e:
                print_line(f"Error: {e}")
            return True
        if sub == "delete":
            if len(args) < 2:
                print_line("Usage: note delete <id>")
                return True
            found = self.notes.delete_note(args[1])
            print_line("Deleted" if found else "Note not found")
            return True
        suggestion = suggest_command("note " + sub)
        print_line(f"Unknown note subcommand. {('Did you mean: ' + suggestion) if suggestion else 'Type: help'}")
        return True


def run_repl() -> None:
    app = App()
    print_line("Personal Assistant CLI. Type 'help' to see commands. Ctrl+C to exit.")
    while True:
        try:
            line = input("assistant> ").strip()
        except (EOFError, KeyboardInterrupt):
            print_line("\nBye!")
            break
        if line == "":
            continue
        keep_running = app.handle_line(line)
        if not keep_running:
            print_line("Bye!")
            break
