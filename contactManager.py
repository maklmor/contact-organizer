import datetime
from tkinter import (
    Button,
    Entry,
    Label,
    Menu,
    Tk,
    Frame,
    LEFT,
    RIGHT,
    Toplevel,
    messagebox,
    ttk,
    filedialog,
    font,
)
from tkinter.constants import BOTTOM, TOP
from typing import Any, List, Dict, Optional, Tuple, Union
import vobject

from multiColumnListbox import MultiColumnListbox
from person import Person
from dao import DAO


def _convert_stringval(value) -> Union[int, str, Any]:
    """
    This is a tweak of original method as it (un?)intentionally tries to change
    the values to int, instead of their original type

    Author: github@Jason Yang
    """
    if hasattr(value, "typename"):
        value = str(value)
        try:
            value = int(value)
        except (ValueError, TypeError):
            pass
    return value


class ContactManager:
    def __init__(self, location: str):
        # Instantiation of Database Access Object -> DAO
        self.dao: DAO = DAO(location)

        # Naming convention constants
        self.NAME: str = "Meno"
        self.BDAY: str = "Narodeniny"
        self.EMAIL: str = "E-mail"
        self.PHONE: str = "Telefónne Číslo"
        self.NOTE: str = "Poznámka"

    def _load_contacts(self, path: str = "") -> List[Person]:
        """Returns a list of persons

        path (str, optional): specifies the path of file to load contacts from
        """
        return self.dao.load(path)

    def _build_gui(self) -> None:
        """Creates new main GUI of ContactManager obj"""
        # Fundamental part - Tk
        self.window: Tk = Tk()
        self.window.title("Contact Manager")
        self.window.geometry("900x400")

        # Changing the default tk font (original seems too small to me)
        defaultFont = font.nametofont("TkDefaultFont")
        defaultFont.configure(size=13)

        # Create main Frames
        self.listbox_frame = Frame()
        self.listbox_frame.pack(fill="both", side=BOTTOM, expand=True)
        self.menu_frame = Frame()
        self.menu_frame.pack(fill="both", side=TOP)

        # Build main parts of the GUI
        self._build_listbox()
        self._build_menus()

        # Create bday reminder popup alert
        if self.have_bday_today != []:
            message = "Dnes má narodeniny:\n{}".format(
                self.have_bday_today.pop()
            )
            for celebrant in self.have_bday_today:
                message += ", " + celebrant
            messagebox.showwarning("Narodeniny", message)

        # Mainloop to make sure it's working as intended
        self.window.mainloop()

    def _build_listbox(self) -> None:
        """Instantiate self.listbox - contacts preloaded, MultiColumnListbox"""
        self.listbox: MultiColumnListbox = MultiColumnListbox(
            self.listbox_frame,
            [self.NAME, self.BDAY, self.EMAIL, self.PHONE, self.NOTE],
        )
        self.listbox.load_data([x.get_tuple_data() for x in self.contacts])

    def _build_menus(self) -> None:
        """Instantiates and populates menu bar with functional elements"""
        # Menus
        menu_bar = Menu(self.menu_frame)
        self.window.config(menu=menu_bar)
        action_menu = Menu(menu_bar, tearoff=0)
        display_menu = Menu(menu_bar, tearoff=0)

        # Add read, update, delete, import, export buttons
        action_menu.add_command(
            label="Pridať nový kontakt", command=self._create_contact
        )
        action_menu.add_command(
            label="Upraviť kontakt", command=self._edit_contact
        )
        action_menu.add_command(
            label="Vymazať kontakt", command=self._delete_contact
        )
        action_menu.add_command(
            label="Importovať kontakty z VCard 3.0 súboru",
            command=self._import_contacts,
        )
        action_menu.add_command(
            label="Exportovať kontakty do VCard 3.0 súboru",
            command=self._export_contacts,
        )
        menu_bar.add_cascade(label="Možnosti", menu=action_menu)

        # Add checkbuttons to the control what data is being displayed
        display_menu.add_checkbutton(
            label=self.NAME,
            variable=self.listbox.columns[self.NAME],
            command=self.listbox.edit_column_displayment,
        )
        display_menu.add_checkbutton(
            label=self.BDAY,
            variable=self.listbox.columns[self.BDAY],
            command=self.listbox.edit_column_displayment,
        )
        display_menu.add_checkbutton(
            label=self.EMAIL,
            variable=self.listbox.columns[self.EMAIL],
            command=self.listbox.edit_column_displayment,
        )
        display_menu.add_checkbutton(
            label=self.PHONE,
            variable=self.listbox.columns[self.PHONE],
            command=self.listbox.edit_column_displayment,
        )
        display_menu.add_checkbutton(
            label=self.NOTE,
            variable=self.listbox.columns[self.NOTE],
            command=self.listbox.edit_column_displayment,
        )
        menu_bar.add_cascade(label="Zobrazené údaje", menu=display_menu)

        # Add search button
        menu_bar.add_command(label="Vyhľadať", command=self._search_contact)

    def _create_contact(self) -> None:
        """Commands the initiation of contact creation process"""
        self._build_contact_creator()

    def _build_contact_creator(self) -> None:
        """Create new window and handle the user input of a new contact"""
        # New window
        self.contact_creator_window = Toplevel()

        # Create name label and entry field
        name_label = Label(self.contact_creator_window, text=self.NAME)
        name_label.pack()
        name_field = Entry(self.contact_creator_window, width=30)
        name_field.pack(padx=50)

        # Create bday label and entry field
        bday_label = Label(self.contact_creator_window, text=self.BDAY)
        bday_label.pack()
        bday_field = Entry(self.contact_creator_window, width=30)
        bday_field.pack(padx=50)

        # Create email label and entry field
        email_label = Label(self.contact_creator_window, text=self.EMAIL)
        email_label.pack()
        email_field = Entry(self.contact_creator_window, width=30)
        email_field.pack(padx=50)

        # Create phone label and entry field
        phone_label = Label(self.contact_creator_window, text=self.PHONE)
        phone_label.pack()
        phone_field = Entry(self.contact_creator_window, width=30)
        phone_field.pack(padx=50)

        # Create note label and entry field
        note_label = Label(self.contact_creator_window, text=self.NOTE)
        note_label.pack()
        note_field = Entry(self.contact_creator_window, width=30)
        note_field.pack(padx=50)

        # Create submit button
        submit_button = Button(
            self.contact_creator_window,
            text="Pridať nový kontakt",
            command=self._request_contact_save,
        )
        submit_button.pack()

    def _request_contact_save(self) -> None:
        """Handles requests to save a single contact

        Collects data of the new person from the contact_creator_window,
        validates it and then saves it
        """
        # Collection of data from Entry widgets of the contact_creator_window
        args = []
        for widget in self.contact_creator_window.winfo_children():
            if type(widget) == Entry:
                args.append(widget.get())
        new_person = Person(*args)

        # Validate the data, pass them to the DAO and add among loaded contacts
        if new_person.validate():
            self.dao.save(new_person)
            self.contacts.append(new_person)

            # Reload the listbox and destroy the contact_creator_window
            self.listbox.load_data([x.get_tuple_data() for x in self.contacts])
            self.contact_creator_window.destroy()
        else:
            messagebox.showerror(
                "Error",
                "Niektorý z údajov nie je platný!\n"
                "Prekontrolujte ich a skúste to ešte raz!"
                "Prekontrolujte ich a skúste to ešte raz!\n"
                "(Formát narodenín je YYYY-MM-DD, email je"
                " username@domain.top_domain) a telefónne číslo môže začínať"
                "+ a potom musia nasledovať jedine cifry a medzery",
            )

    def _request_multiple_contact_save(
        self, contacts_to_save: List[Person] = []
    ) -> None:
        """Handles requests to save contacts

        contacts_to_save (List[Person], optional): if this list is populated,
        each member of the list will serve as a source of data and be saved if
        valid
        """
        # Validate the data, pass them to the DAO and add among loaded contacts
        for contact in contacts_to_save:
            if contact.validate():
                self.dao.save(contact)
                self.contacts.append(contact)

                # Reload the listbox
                self.listbox.load_data(
                    [x.get_tuple_data() for x in self.contacts]
                )
            else:
                messagebox.showerror(
                    "Error",
                    "Niektorý z údajov nie je platný!\n"
                    "Prekontrolujte ich a skúste to ešte raz!",
                )

    def _edit_contact(self) -> None:
        """Commands the initiation of contact edit process"""
        # Instantiate the user selected person in listbox
        self.person_being_edited = self._get_selected_person()
        self._build_contact_editor()

    def _build_contact_editor(self) -> None:
        """Create new window and handle the contact editing"""
        # New window
        self.contact_editor_window = Toplevel()

        # Create name label and entry field
        name_label = Label(self.contact_editor_window, text=self.NAME)
        name_label.pack()
        name_field = Entry(self.contact_editor_window, width=30)
        name_field.insert(0, self.person_being_edited.name)
        name_field.pack(padx=50)

        # Create bday label and entry field
        bday_label = Label(self.contact_editor_window, text=self.BDAY)
        bday_label.pack()
        bday_field = Entry(self.contact_editor_window, width=30)
        bday_field.insert(0, self.person_being_edited.bday)
        bday_field.pack(padx=50)

        # Create email label and entry field
        email_label = Label(self.contact_editor_window, text=self.EMAIL)
        email_label.pack()
        email_field = Entry(self.contact_editor_window, width=30)
        email_field.insert(0, self.person_being_edited.email)
        email_field.pack(padx=50)

        # Create phone label and entry field
        phone_label = Label(self.contact_editor_window, text=self.PHONE)
        phone_label.pack()
        phone_field = Entry(self.contact_editor_window, width=30)
        phone_field.insert(0, self.person_being_edited.phone)
        phone_field.pack(padx=50)

        # Create note label and entry field
        note_label = Label(self.contact_editor_window, text=self.NOTE)
        note_label.pack()
        note_field = Entry(self.contact_editor_window, width=30)
        note_field.insert(0, self.person_being_edited.note)
        note_field.pack(padx=50)

        # Create submit button
        submit_button = Button(
            self.contact_editor_window,
            text="Upraviť kontakt",
            command=self._request_contact_edit,
        )
        submit_button.pack()

    def _request_contact_edit(self) -> None:
        """Handles requests to edit a contact

        Collects data of the edited person from the contact_editor_window,
        validates it and then saves it
        """
        # Collection of data from Entry widgets of the contact_creator_window
        args = []
        for widget in self.contact_editor_window.winfo_children():
            if type(widget) == Entry:
                args.append(widget.get())
        person = Person(*args)

        # Validate the new data
        if person.validate():
            # Pass the new data to the DAO and save it, delete the old one
            self.dao.save(person)
            self.dao._delete_contact(self.person_being_edited)

            # Reload the contacts and listbox, destroy the window
            self.contacts = self._load_contacts()
            self.listbox.load_data([x.get_tuple_data() for x in self.contacts])
            self.contact_editor_window.destroy()
        else:
            messagebox.showerror(
                "Error",
                "Niektorý z údajov nie je platný!\n"
                "Prekontrolujte ich a skúste to ešte raz!\n"
                "(Formát narodenín je YYYY-MM-DD, email je"
                " username@domain.top_domain) a telefónne číslo môže začínať"
                "+ a potom musia nasledovať jedine cifry a medzery",
            )

    def _delete_contact(self) -> None:
        """Commands the initiation of contact deletion process"""
        # Instatiate the person selected in listbox
        person = self._get_selected_person()

        # Pop up a deletion confirmation window
        if messagebox.askyesno(
            "Warning",
            "Naozaj si prajete vymazať nasledujúci kontakt:\n{}?".format(
                person.name
            ),
        ):
            # Delete the contact, reload the contacts and listbox
            self.dao._delete_contact(person)
            self.contacts = self._load_contacts()
            self.listbox.load_data([x.get_tuple_data() for x in self.contacts])

    def _import_contacts(self) -> None:
        """Commands the initiation of contact import process

        Opens the file dialog where user picks a file to import from,
        loads the contacts from the path returned by the file dialog
        and request the DAO to save them
        """
        import_path = filedialog.askopenfilename()
        new_contacts = self._load_contacts(import_path)
        self._request_multiple_contact_save(new_contacts)

    def _export_contacts(self) -> None:
        """Commands the initiation of contact export process

        opens the file save dialog where user picks a file to export to,
        passes the target location to the DAO
        """
        export_path = filedialog.asksaveasfilename()
        self.dao.export_contacts(export_path)

    def _search_contact(self) -> None:
        """Commands the initiation of contact search process"""
        self._build_contact_searcher()

    def _build_contact_searcher(self) -> None:
        """Creates new window and handles the contact search"""
        # New window
        self.contact_searcher_window = Toplevel()

        # Create search bar label and entry field
        search_label = Label(
            self.contact_searcher_window,
            text="Zadajte meno hľadaného kontaktu",
        )
        search_label.pack()
        search_field = Entry(self.contact_searcher_window, width=30)
        search_field.pack(padx=50)

        # Create submit button
        submit_button = Button(
            self.contact_searcher_window,
            text="Hľadať",
            command=self._request_contact_search,
        )
        submit_button.pack()

    def _request_contact_search(self) -> None:
        """Handles request to search a contact"""
        self.person_being_searched: Optional[Person] = None
        searched_name = None

        # Collect the search bar name input
        for widget in self.contact_searcher_window.winfo_children():
            if type(widget) == Entry:
                searched_name = widget.get()

        # Check whether the entered name exists
        for person in self.contacts:
            if person.name == searched_name:
                self.person_being_searched = person

        # If the person was found, destroy the search window, build the viewer
        if self.person_being_searched is not None:
            self.contact_searcher_window.destroy()
            self._build_contact_viewer()
        else:
            messagebox.showerror(
                "Error",
                "Zadané meno sa v databáze nepodarilo nájsť,"
                " skontrolujte ho a skúste to ešte raz!",
            )

    def _build_contact_viewer(self) -> None:
        """Creates new window and displays the data of searched person"""
        # New window
        window = Toplevel()
        window.title("Vyhľadaný kontakt")

        # Create the labels and fill them with the searched person data
        name_label = Label(window, text=self.person_being_searched.name)
        name_label.pack(padx=50)
        bday_label = Label(window, text=self.person_being_searched.bday)
        bday_label.pack(padx=50)
        email_label = Label(window, text=self.person_being_searched.email)
        email_label.pack(padx=50)
        phone_label = Label(window, text=self.person_being_searched.phone)
        phone_label.pack(padx=50)
        note_label = Label(window, text=self.person_being_searched.note)
        note_label.pack(padx=50)

    def _get_selected_person(self) -> Person:
        """Instantiates and returns the selected person in the listbox"""
        args = self.listbox.selected_contact["values"]
        return Person(*args)

    def _check_bday(self) -> None:
        """Checks the bday of all the contacts in the database"""
        # If no contacts are present stop checking
        self.have_bday_today = []
        if self.contacts == []:
            return

        # Get today's date
        current_date = datetime.datetime.today().strftime("%m-%d")

        # Check every contact's bday
        for contact in self.contacts:
            try:
                bday_date = contact.bday.split("-", 1)[1]
            except Exception:
                continue
            if bday_date == current_date:
                self.have_bday_today.append(contact.name)

    def main(self) -> None:
        """Loads up the contacts and builds the GUI of the ContactManager"""
        # This switches the original method for a tweaked one
        ttk._convert_stringval = _convert_stringval

        # Prepares contact list containing all persons to display
        self.contacts = self._load_contacts()

        # Check who has bday
        self._check_bday()

        # Prepares main GUI
        self._build_gui()


if __name__ == "__main__":
    # Default location of txt file serving as a database
    db_location = "db.txt"

    # Entry point to the app
    contactManager = ContactManager(db_location)
    contactManager.main()
