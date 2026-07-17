"""
CalendarApp — simulates a calendar with events and scheduling.

Tools:
  - list_events (READ): list all calendar events
  - get_event (READ): get details of a specific event
  - create_event (WRITE): create a new calendar event
  - update_event (WRITE): update an existing event
  - delete_event (WRITE): delete a calendar event
  - check_conflicts (READ): check for scheduling conflicts at a given time
"""

from runtime.apps.app import App, tool
from uuid import uuid4


class CalendarApp(App):

    def __init__(self):
        super().__init__()
        self.events = {}

    @classmethod
    def from_config(cls, initial_state):
        instance = cls()
        for event in initial_state.get("events", []):
            eid = event.get("id", str(uuid4())[:8])
            instance.events[eid] = {
                "id": eid,
                "title": event["title"],
                "date": event["date"],
                "start_time": event["start_time"],
                "end_time": event["end_time"],
                "attendees": event.get("attendees", []),
                "location": event.get("location", ""),
                "description": event.get("description", ""),
            }
        return instance

    @tool()
    def list_events(self) -> str:
        """List all events in the calendar. Returns a summary of each event with id, title, date, time and attendees."""
        if not self.events:
            return "Calendar is empty."
        lines = []
        for eid, ev in self.events.items():
            attendees = ", ".join(ev["attendees"]) if ev["attendees"] else "none"
            lines.append(
                f"[{eid}] {ev['title']} | {ev['date']} {ev['start_time']}-{ev['end_time']} | "
                f"Location: {ev['location'] or 'TBD'} | Attendees: {attendees}"
            )
        return "\n".join(lines)

    @tool()
    def get_event(self, event_id: str) -> str:
        """Get full details of a specific calendar event by its ID.
        Args:
            event_id: The unique identifier of the calendar event.
        Returns:
            All details of the event including title, date, time, location, attendees and description.
        """
        ev = self.events.get(event_id)
        if not ev:
            return f"Event '{event_id}' not found."
        attendees = ", ".join(ev["attendees"]) if ev["attendees"] else "none"
        return (
            f"Title: {ev['title']}\n"
            f"Date: {ev['date']}\n"
            f"Time: {ev['start_time']} - {ev['end_time']}\n"
            f"Location: {ev['location'] or 'TBD'}\n"
            f"Attendees: {attendees}\n"
            f"Description: {ev['description']}"
        )

    @tool()
    def create_event(self, title: str, date: str, start_time: str, end_time: str,
                     attendees: str = "", location: str = "", description: str = "") -> str:
        """Create a new calendar event.
        Args:
            title: The event title.
            date: The event date (format: YYYY-MM-DD).
            start_time: Start time (format: HH:MM).
            end_time: End time (format: HH:MM).
            attendees: Comma-separated list of attendee names (optional).
            location: Event location (optional).
            description: Event description (optional).
        Returns:
            Confirmation with the created event's ID.
        """
        eid = str(uuid4())[:8]
        attendee_list = [a.strip() for a in attendees.split(",") if a.strip()] if attendees else []
        self.events[eid] = {
            "id": eid,
            "title": title,
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "attendees": attendee_list,
            "location": location,
            "description": description,
        }
        return f"Event '{title}' created on {date} {start_time}-{end_time}. ID: {eid}"

    @tool()
    def update_event(self, event_id: str, title: str = "", date: str = "", start_time: str = "",
                     end_time: str = "", attendees: str = "", location: str = "", description: str = "") -> str:
        """Update fields of an existing calendar event. Only non-empty fields are updated.
        Args:
            event_id: The ID of the event to update.
            title: New title (leave empty to keep current).
            date: New date (leave empty to keep current).
            start_time: New start time (leave empty to keep current).
            end_time: New end time (leave empty to keep current).
            attendees: New comma-separated attendees (leave empty to keep current).
            location: New location (leave empty to keep current).
            description: New description (leave empty to keep current).
        Returns:
            Confirmation of the update.
        """
        ev = self.events.get(event_id)
        if not ev:
            return f"Event '{event_id}' not found. Cannot update."
        if title: ev["title"] = title
        if date: ev["date"] = date
        if start_time: ev["start_time"] = start_time
        if end_time: ev["end_time"] = end_time
        if attendees: ev["attendees"] = [a.strip() for a in attendees.split(",") if a.strip()]
        if location: ev["location"] = location
        if description: ev["description"] = description
        return f"Event '{ev['title']}' (ID: {event_id}) updated successfully."

    @tool()
    def delete_event(self, event_id: str) -> str:
        """Delete a calendar event by its ID.
        Args:
            event_id: The ID of the event to delete.
        Returns:
            Confirmation of deletion or error if not found.
        """
        if event_id in self.events:
            title = self.events[event_id]["title"]
            del self.events[event_id]
            return f"Event '{title}' (ID: {event_id}) deleted."
        return f"Event '{event_id}' not found."

    @tool()
    def check_conflicts(self, date: str, start_time: str, end_time: str) -> str:
        """Check if a proposed time slot conflicts with existing events.
        Args:
            date: The date to check (format: YYYY-MM-DD).
            start_time: Proposed start time (format: HH:MM).
            end_time: Proposed end time (format: HH:MM).
        Returns:
            List of conflicting events, or confirmation that the slot is free.
        """
        conflicts = []
        for eid, ev in self.events.items():
            if ev["date"] == date:
                if not (end_time <= ev["start_time"] or start_time >= ev["end_time"]):
                    conflicts.append(f"[{eid}] {ev['title']} ({ev['start_time']}-{ev['end_time']})")
        if conflicts:
            return "Conflicts found:\n" + "\n".join(conflicts)
        return f"No conflicts for {date} {start_time}-{end_time}. Slot is available."