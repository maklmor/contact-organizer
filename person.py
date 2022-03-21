from typing import List, Optional, Tuple
import re


class Person:
    def __init__(
        self,
        name: str,
        bday: str = "",
        email: str = "",
        phone: str = "",
        note: str = "",
    ):
        self.name = name
        self.bday = bday
        self.email = email
        self.phone = phone
        self.note = note

    def get_tuple_data(self) -> Tuple[str]:
        """
        Return information about this person as a tuple
        """
        return (self.name, self.bday, self.email, self.phone, self.note)

    def validate(self) -> bool:
        """
        Note: The definition of what a valid email address should look like
        is a little bit incomplete in my opinion (especially missing
        specification of allowed characters), but anyway, I'm checking it
        according to the task:
        any_characters@any_characters.any_characters
        """
        # Email validation
        if self.email != "":
            try:
                username, reminder = self.email.split("@", 1)
            except ValueError:
                return False
            if username == "":
                return False
            domain_name, top_lvl_domain = reminder.split(".", 1)
            if domain_name == "" or top_lvl_domain == "":
                return False

        # Phone validation
        if (
            not re.compile("^+?[ 0123456789]+$").match(self.phone)
            and self.phone != ""
        ):
            return False

        # Bday validation
        if self.bday != "":
            year = None
            month = None
            day = None
            try:
                year, month, day = self.bday.split("-")
            except Exception:
                return False

            # Check if it's a valid year
            if not re.compile("^[0-9]+$").match(year):
                return False

            # Check if it's a valid month
            if month not in [
                "01",
                "02",
                "03",
                "04",
                "05",
                "06",
                "07",
                "08",
                "09",
                "10",
                "11",
                "12",
            ]:
                return False

            # Check if it's a valid day
            if (
                not re.compile("^0[1-9]$").match(day)
                and not re.compile("^[12][0-9]$").match(day)
                and not re.compile("^3[01]$").match(day)
            ):
                return False

            # Check if the day matches the it's month maximum
            if int(month) in [4, 6, 9, 11] and day == "31":
                return False

            # Check if it doesn't break the "February rule"
            if month == "02" and int(day) > 28 and int(year) % 4 != 0:
                return False
            if month == "02" and int(day) > 29 and int(year) % 4 == 0:
                return False
        return True
