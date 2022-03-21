from tkinter import BooleanVar, Scrollbar, ttk, Frame, font
from typing import Dict, List, Optional, Tuple, Union, Any
from collections import OrderedDict


class MultiColumnListbox:
    def __init__(self, container: Frame, column_names: List[str]):
        # The main Treeview object
        self.tree: ttk.Treeview = None

        # The main Frame container
        self.container = container

        # Placeholders for the column names
        self.columns: OrderedDict[str, BooleanVar] = OrderedDict()
        self.columns[column_names[0]] = BooleanVar(value=True)
        self.columns[column_names[1]] = BooleanVar(value=True)
        self.columns[column_names[2]] = BooleanVar(value=True)
        self.columns[column_names[3]] = BooleanVar(value=True)
        self.columns[column_names[4]] = BooleanVar(value=True)

        # Represents the data of the selected item of self.tree
        self.selected_contact: Optional[Dict] = None

        # Build the object
        self._setup()

    def _setup(self) -> None:
        """
        Prepare a Treeview object so it behaves as a MultiColumnListbox
        """
        # Treeview (MultiColumnListbox)
        self.tree = ttk.Treeview(
            columns=list(self.columns.keys()), show="headings"
        )
        vertical_scrollbar = Scrollbar(
            orient="vertical", command=self.tree.yview
        )
        horizontal_scrollbar = Scrollbar(
            orient="horizontal", command=self.tree.xview
        )

        # Mapping listbox's functions to external scrollbars
        self.tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        # Append elements to the grid
        self.tree.grid(column=0, row=0, sticky="nsew", in_=self.container)
        vertical_scrollbar.grid(
            column=1, row=0, sticky="ns", in_=self.container
        )
        horizontal_scrollbar.grid(
            column=0, row=1, sticky="ew", in_=self.container
        )

        # Configure listbox + scrollbars to be auto-resizing
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # Setup headings of the MultiColumnListbox
        for column in list(self.columns.keys()):
            self.tree.heading(
                column, text=column, command=lambda c=column: self.sort(c, 0)
            )
            self.tree.column(column, width=100)

        # Capture selected item
        self.tree.bind("<ButtonRelease-1>", func=self._select_contact)

    def _select_contact(self, event) -> None:
        """
        Save the last selected item in the table
        """
        focus = self.tree.focus()
        self.selected_contact = self.tree.item(focus)

    def load_data(self, data: List[Union[List[Any], Tuple[Any]]]) -> None:
        """
        Load data into the MultiColumnListbox
        """
        # Make sure the data will be consistent and available later on
        self.data = data

        # Flush whole listbox to prevent data poisoning
        self.tree.delete(*self.tree.get_children())

        # Load data
        for item in self.data:
            self.tree.insert("", "end", values=item)

            # Adjust the width of column to fit the contents if neccessary
            for x, content in enumerate(item):
                column_width = font.Font().measure(content)
                if (
                    self.tree.column(list(self.columns.keys())[x], width=None)
                    < column_width
                ):
                    self.tree.column(
                        list(self.columns.keys())[x], width=column_width
                    )

    def sort(self, column: str, descending: int) -> None:
        """
        Sorting of the columns by value
        """
        # Get the data out of the column
        data = [
            (self.tree.set(child, column), child)
            for child in self.tree.get_children("")
        ]

        # Sort the data
        data.sort(reverse=descending, key=lambda x: x[0].lower())

        # Move the rows accordingly
        for ix, item in enumerate(data):
            self.tree.move(item[1], "", ix)

        # Switch the heading so it will sort in the opposite direction
        self.tree.heading(
            column,
            command=lambda column=column: self.sort(
                column, int(not descending)
            ),
        )

    def edit_column_displayment(self) -> None:
        """
        Edit visibility of certain columns according to self.columns
        """
        self.tree["displaycolumns"] = [
            x[0] for x in self.columns.items() if x[1].get()
        ]
