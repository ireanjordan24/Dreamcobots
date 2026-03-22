"""
Feature 2: Real estate viewing scheduler.

Allows users and agents to schedule, reschedule, and cancel property viewings.
Maintains an in-memory appointment calendar keyed by property address.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta


class ViewingScheduler:
    """Manages property viewing appointments."""

    AVAILABLE_SLOTS_PER_DAY = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00"]

    def __init__(self):
        # {appointment_id: {address, date, time, agent, buyer, status}}
        self._appointments: dict = {}
        self._next_id = 1

    def _make_id(self) -> str:
        aid = f"APT{self._next_id:04d}"
        self._next_id += 1
        return aid

    def schedule_viewing(self, address: str, date: str, time_slot: str,
                         buyer_name: str, agent_name: str = "Unassigned") -> dict:
        """Schedule a property viewing. Returns the appointment record.

        Args:
            address:    Property address.
            date:       Date string 'YYYY-MM-DD'.
            time_slot:  Time string 'HH:MM'.
            buyer_name: Name of the prospective buyer.
            agent_name: Name of the listing/buyer's agent.
        """
        # Validate no double-booking
        for appt in self._appointments.values():
            if appt["address"] == address and appt["date"] == date and appt["time"] == time_slot:
                if appt["status"] == "confirmed":
                    raise ValueError(f"Slot {date} {time_slot} at {address} is already booked.")

        aid = self._make_id()
        record = {
            "appointment_id": aid,
            "address": address,
            "date": date,
            "time": time_slot,
            "buyer": buyer_name,
            "agent": agent_name,
            "status": "confirmed",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self._appointments[aid] = record
        return dict(record)

    def cancel_viewing(self, appointment_id: str) -> dict:
        """Cancel a scheduled viewing. Returns updated record."""
        if appointment_id not in self._appointments:
            raise KeyError(f"Appointment {appointment_id} not found.")
        self._appointments[appointment_id]["status"] = "cancelled"
        return dict(self._appointments[appointment_id])

    def reschedule_viewing(self, appointment_id: str, new_date: str, new_time: str) -> dict:
        """Reschedule an existing viewing to a new date/time."""
        if appointment_id not in self._appointments:
            raise KeyError(f"Appointment {appointment_id} not found.")
        appt = self._appointments[appointment_id]
        appt["date"] = new_date
        appt["time"] = new_time
        appt["status"] = "rescheduled"
        return dict(appt)

    def get_appointments(self, address: str = None, buyer: str = None) -> list:
        """Return all appointments, optionally filtered by address or buyer."""
        results = list(self._appointments.values())
        if address:
            results = [a for a in results if address.lower() in a["address"].lower()]
        if buyer:
            results = [a for a in results if buyer.lower() in a["buyer"].lower()]
        return [dict(a) for a in results if a["status"] != "cancelled"]

    def get_available_slots(self, address: str, date: str) -> list:
        """Return available time slots for a property on a given date."""
        booked = {
            a["time"]
            for a in self._appointments.values()
            if a["address"] == address and a["date"] == date and a["status"] == "confirmed"
        }
        return [s for s in self.AVAILABLE_SLOTS_PER_DAY if s not in booked]

    def get_upcoming_viewings(self, days_ahead: int = 7) -> list:
        """Return confirmed viewings scheduled within the next N days."""
        today = datetime.now().date()
        cutoff = today + timedelta(days=days_ahead)
        results = []
        for appt in self._appointments.values():
            if appt["status"] in ("confirmed", "rescheduled"):
                try:
                    appt_date = datetime.strptime(appt["date"], "%Y-%m-%d").date()
                    if today <= appt_date <= cutoff:
                        results.append(dict(appt))
                except ValueError:
                    pass
        return sorted(results, key=lambda x: (x["date"], x["time"]))