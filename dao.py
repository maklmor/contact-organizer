from typing import List
import vobject
import shutil

from person import Person


class DAO:
    def __init__(self, default_path: str):
        # A path to the default database
        self.default_path: str = default_path

        # Default encoding of the database's files
        self.ENCODING: str = "UTF-8"

        # Default newline characters: serves as a fix for a bug when
        # the database was conflicting with vObject serialization ...
        self.NEWLINE: str = ""

    def load(self, path: str = "") -> List[Person]:
        """Load contacts from the database

        path (str, optional): specify path to load from,
        otherwise load from the default file specified by self.default_path
        """
        person_list = []
        path = self.default_path if path == "" else path

        with open(path, encoding=self.ENCODING, newline=self.NEWLINE) as file:
            # Read the database and create a vCard iterator
            file_string = file.read()
            vcard_iterator = vobject.readComponents(file_string)
            vcard = next(vcard_iterator, None)

            # From vCard iterator extract the data to contruct a Person obj
            while vcard:
                try:
                    name = vcard.contents["fn"][0].value
                except KeyError:
                    continue
                try:
                    bday = vcard.contents["bday"][0].value
                except KeyError:
                    bday = None
                try:
                    email = vcard.contents["email"][0].value
                except KeyError:
                    email = None
                try:
                    phone = vcard.contents["tel"][0].value
                except KeyError:
                    phone = None
                try:
                    note = vcard.contents["note"][0].value
                except KeyError:
                    note = None

                # Person instantiation
                attrs = [
                    x
                    for x in (name, bday, email, phone, note)
                    if x is not None
                ]
                if attrs != []:
                    person_list.append(Person(*attrs))

                vcard = next(vcard_iterator, None)
        return person_list

    def save(self, person: Person) -> None:
        """Save the specified person to the database

        person (Person): person to save
        """
        # Get a vCard string representation of a Person obj, save it
        vcard_str = self._transform_person_to_vcard_string(person)
        with open(
            self.default_path,
            "a",
            encoding=self.ENCODING,
            newline=self.NEWLINE,
        ) as file:
            file.write(vcard_str)

    def _transform_person_to_vcard_string(self, person: Person) -> str:
        """Transforms a Person obj to a vCard standardized string

        person (Person): a Person obj to transform
        """
        # Create vCard fields to fill in later
        vcard = vobject.vCard()
        vcard.add("n")
        vcard.add("fn")
        vcard.add("bday")
        vcard.add("email")
        vcard.add("tel")
        vcard.add("note")

        # Fill in the attributes of the person
        vcard.n.value = vobject.vcard.Name(family="", given="")
        vcard.fn.value = person.name
        vcard.bday.value = person.bday
        vcard.email.value = person.email
        vcard.tel.value = person.phone
        vcard.note.value = person.note

        # Generate and return the vCard string
        return vcard.serialize()

    def _delete_contact(self, person: Person) -> None:
        """Deletes a specified Person obj from the database

        person (Person): a Person obj to delete
        """
        # Generates a vCard string for the given person
        vcard_str = self._transform_person_to_vcard_string(person)
        with open(
            self.default_path,
            "r+",
            encoding=self.ENCODING,
            newline=self.NEWLINE,
        ) as file:
            # Reads the database
            text = file.read()

            # Finds the part to remove and substitues it for a empty string
            new_db = text.replace(vcard_str, "", 1)

            """
            Rewrite the database with a version where the person is no longer
            present
            """
            file.seek(0)
            file.write(new_db)
            file.truncate()

    def export_contacts(self, export_path: str) -> None:
        """Exports the contacts to another file

        As far as the DAO preserves the database in vCard format,
        export of the contacts is as simple as copying the original file
        to another location

        export_path (str): represents the target location to export data to
        """
        shutil.copyfile(self.default_path, export_path)
