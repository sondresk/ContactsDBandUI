import io
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from tkinter import filedialog

text_font = ("Calibri", 12)
bg_color = "white"
inner_w_width = 1000


def write_to_file(data: bytes, filename: str, filetype: str, save_path: str = ''):
    """
    Saves data stored as bytes to the proper file format \n
    :param data: The binary data to be stored
    :param filename: Name of the file without file type.
    :param filetype: The type of file to be saved as without the period - 'png' etc.
    :param save_path: Optional relative or absolute path where picture should be stored
    """
    filename = save_path + filename + "." + filetype
    with open(filename, "wb") as file:
        file.write(data)
    print("Stored picture into:\t", filename, "\n")


def read_picture_from_db(cursor, contact_name: str, filetype: str, save_path: str = '', ):
    """
    Read pictures stored as bytes in a database and saves them in a .png format

    :param cursor: A sqlite3 database connection like a cursor object
    :param contact_name: The name of the contact whom the function is retrieving the picture for
    :param filetype: The type of file to be saved as without the period - 'png' etc.
    :param save_path: Optional relative or absolute path where picture should be stored
    :return: None
    """
    for name, photo in cursor.execute(f"SELECT name, photo FROM contacts WHERE photo IS NOT NULL AND name = ?",
                                      (contact_name,)):
        name = save_path + name + ".png"
        write_to_file(photo, name, filetype, save_path)


def convert_to_binary(filepath: str) -> bytes:
    """Converts digital data to binary. Used for storing pictures etc. in database."""
    try:
        with open(filepath, "rb") as file:
            blob_data = file.read()
        return blob_data
    except TypeError:
        if not is_nan(filepath):
            print(f"------! The provided path for '{filepath}' doesn't work.")


def is_nan(num):
    return num != num


def set_img_size(init_w, init_h):
    h = 400
    factor = h / init_h
    w = round(init_w * factor)
    if w > 970:
        w = 970
        h = round(init_h * (w / init_w))
    return w, h


class StartUpApp(tk.Tk):
    def __init__(self, bg=bg_color, *args, **kwargs):
        self.root = tk.Tk.__init__(self, *args, **kwargs)
        self.configure(bg=bg)
        self.choice_label = tk.Label(self.root, text="What do you want to do?", font=text_font, bg=bg)
        self.choice_label.pack(padx=5, pady=15)

        style = ttk.Style()
        style.configure(".", font=text_font, background=bg_color)

        self.buttons_frame = tk.Frame(self.root, bg=bg)
        self.buttons_frame.pack(padx=5, pady=5)

        self.add_button = ttk.Button(self.buttons_frame, text="Add Contact", width=20,
                                     command=self._add_contact)
        self.add_button.pack(side="left", padx=5, pady=5)

        self.view_edit_button = ttk.Button(self.buttons_frame, text="View and Edit Contact", width=20,
                                           command=self._view_edit)
        self.view_edit_button.pack(side="right", padx=5, pady=5)

        self.bind_class("TButton", "<Return>", lambda event: event.widget.invoke())
        self.add_button.focus()

    def _add_contact(self):
        self.destroy()
        add_contact_app = AddContactApp()
        add_contact_app.mainloop()

    def _view_edit(self):
        self.destroy()
        display_edit_app = DisplayAndEdit()
        display_edit_app.mainloop()


class ContactsContainer:
    def __init__(self):
        self.name = ""
        self.email = ""
        self.phone = ""
        self.address = ""
        self.photo = None   # Stored as binary, not as path to the photo
        self.birth_date = ""
        self.occupation = ""
        self.notes = ""

        self._db_connection = None
        self._cursor = None
        self.name_list = self._get_all_names()

    def get_contact(self, search_name):
        if self._db_connection is None:
            self.open_connection()

        self._cursor = self._db_connection.cursor()

        sql_result = self._cursor.execute("SELECT name, IFNULL(email, ''), IFNULL(phone, ''), IFNULL(address, ''), photo,"
                                          " IFNULL(birth_date, ''), IFNULL(occupation, ''), IFNULL(notes, '')"
                                          " FROM contacts WHERE name LIKE ?", ("%" + search_name + "%",))
        found_contacts = (x for x in sql_result)

        try:
            self.name, self.email, self.phone, self.address, self.photo, self.birth_date, \
                self.occupation, self.notes = next(found_contacts)
            try:
                next(found_contacts)
                print("------! More than one contact was found.")  # TODO: Create a popup window with all results?
            except StopIteration:
                pass
        except StopIteration:
            print("------! No contact was found. Either it doesn't exist or the name was misspelled.")

        self._cursor.close()

    def update_contact(self, search_name):
        if self._db_connection is None:
            self.open_connection()

        self._cursor = self._db_connection.cursor()

        self._cursor.execute("UPDATE contacts SET name = ?, email = ?, phone = ?, address = ?, photo = ?, "
                             "birth_date = ?, occupation = ?, notes = ? WHERE name LIKE ?",
                             (self.name, self.email, self.phone, self.address, self.photo, self.birth_date,
                              self.occupation, self.notes, "%" + search_name + "%"))

        self._cursor.connection.commit()
        self._cursor.close()

    def create_contact(self):
        if self._db_connection is None:
            self.open_connection()

        self._cursor = self._db_connection.cursor()

        self._cursor.execute("INSERT INTO contacts (name, email, phone, address, photo, "
                             "birth_date, occupation, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                             (self.name, self.email, self.phone, self.address, self.photo, self.birth_date,
                              self.occupation, self.notes))

        self._cursor.connection.commit()
        self._cursor.close()

    def _get_all_names(self):
        if self._db_connection is None:
            self.open_connection()

        self._cursor = self._db_connection.cursor()

        name_list = []
        for name in self._cursor.execute("SELECT name FROM contacts"):
            name_list.append(name[0])

        self._cursor.close()
        return name_list

    def open_connection(self):
        self._db_connection = sqlite3.connect("contacts.db")

    def close_connection(self):
        self._db_connection.close()
        self._db_connection = None


class VerticalScrolledFrame(tk.Frame):
    def __init__(self, parent, bg=bg_color, *args, **kw):
        super().__init__(parent, bg=bg, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set, bg=bg)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = tk.Frame(self.canvas, bg=bg)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=tk.NW)

        self.interior.bind('<Configure>', self._configure_interior)
        self.interior.bind('<Enter>', self._bound_to_mousewheel)
        self.interior.bind('<Leave>', self._unbound_to_mousewheel)
        self.canvas.bind('<Configure>', self._configure_canvas)

    # track changes to the canvas and frame width and sync them,
    # also updating the scrollbar
    def _configure_interior(self, event):
        # update the scrollbars to match the size of the inner frame
        self.canvas.config(scrollregion=f"0 0 {self.interior.winfo_reqwidth()} {self.interior.winfo_reqheight()}")
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canvas.config(width=self.interior.winfo_reqwidth())

    def _configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the inner frame's width to fill the canvas
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class CustomComboBox(ttk.Combobox):
    def __init__(self, parent, name_list, **kwargs):
        super().__init__(parent, **kwargs)

        self.name_list = name_list

        self.configure(postcommand=lambda: self._on_enter(None))

        self.bind("<Return>", self._on_enter)

    def _on_enter(self, event):
        val_entered = self.get().lower()
        all_names = [name for whole_name in self.name_list for name in whole_name.split()]
        all_names = all_names + self.name_list

        name_contains = []
        for name in all_names:
            if name.lower().startswith(val_entered):
                for whole_name in self.name_list:
                    if name in whole_name:
                        name_contains.append(whole_name)
        name_contains = set(name_contains)  # Remove duplicates

        self.configure(values=tuple(name_contains))

        self.configure(postcommand="")  # Need to temporary disable the postcommand or it will cause a recursion hang
        self.event_generate("<Button-1>")
        self.configure(postcommand=lambda: self._on_enter(None))


class ContactTextWidget(tk.Text):
    def __init__(self, parent, text=None, width=120, height=2, borderwidth=0, bg=bg_color, wrap="word", *args, **kwargs):
        super().__init__(parent, bg=bg, borderwidth=borderwidth, wrap=wrap, width=width, height=height,
                         *args, **kwargs)

        self.insert("end", text)
        self.configure(state="disabled")
        self.tag_add("center", "1.0", "end")
        self.tag_config("center", justify=tk.CENTER)


class ConfirmPopUp:
    def __init__(self, master, text=None, bg=bg_color, font=text_font):
        self.top = tk.Toplevel(master, bg=bg)
        self.master = master

        self.label = tk.Label(self.top, bg=bg, text=text, font=font)
        self.label.pack(padx=10, pady=10)

        style = ttk.Style()
        style.configure(".", font=text_font, background=bg_color)

        self.button_frame = tk.Frame(self.top, bg=bg)
        self.button_frame.pack()

        self.yes_button = ttk.Button(self.button_frame, text="Yes", width=10,
                                     command=self._yes_command)
        self.yes_button.pack(side="left", padx=10, pady=10)
        self.no_button = ttk.Button(self.button_frame, text="No", width=10,
                                    command=self._no_command)
        self.no_button.pack(side="right", padx=10, pady=10)

        self.result = False

        self.top.geometry("+770+400")

        self.top.bind_class("TButton", "<Return>", lambda event: event.widget.invoke())
        self.yes_button.focus()

    def _yes_command(self):
        self.result = True
        self.top.destroy()

    def _no_command(self):
        self.top.destroy()


class DisplayAndEdit(tk.Tk):
    def __init__(self, *args, **kwargs):
        self.root = super().__init__(*args, **kwargs)
        self.configure(bg=bg_color)
        self.state("zoomed")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.frame = VerticalScrolledFrame(self.root)

        canvas_height = self.winfo_screenheight()
        self.frame.canvas.config(height=canvas_height)
        self.frame.pack(fill="x")

        self.popup = None
        self.apply_button = None
        self.cancel_button = None
        self.photo_label = None

        # Creating a contact object which can communicate with database
        self.contact = ContactsContainer()

        # ----- Set custom styles for the ttk widgets -----
        style = ttk.Style()
        style.configure(".", font=text_font, background=bg_color)
        self.option_add("*TCombobox*Listbox*Font", text_font)

        # ----- Contact Search Field -----
        search_field_frame = tk.Frame(self.frame.interior, bg=bg_color)
        search_field_frame.pack(side="top", padx=5, pady=5)

        self.search_field = CustomComboBox(search_field_frame, self.contact.name_list, width=150, font=text_font)
        self.search_field.pack(side="top", padx=5, pady=5)

        separator = ttk.Separator(search_field_frame, orient="horizontal")
        separator.pack(fill="x", pady=15)

        # ===== Buttons =====
        self.buttons_container = tk.Frame(self.frame.interior, bg=bg_color)
        self.buttons_container.pack(side="bottom", padx=5)

        self.edit_button = ttk.Button(self.buttons_container, text="Edit", width=10,
                                      command=self._enter_edit_mode)
        self.edit_button.pack(padx=5, pady=10)

        self.edit_button.configure(state="disabled")

        # ===== info frame =====
        info_frame = tk.Frame(self.frame.interior, bg=bg_color)
        info_frame.pack(side="bottom")

        name_frame = ttk.LabelFrame(info_frame, text="Name")
        name_frame.pack(fill="x", padx=5, pady=5)
        email_frame = ttk.LabelFrame(info_frame, text="Email")
        email_frame.pack(fill="x", padx=5, pady=5)
        phone_frame = ttk.LabelFrame(info_frame, text="Phone number")
        phone_frame.pack(fill="x", padx=5, pady=5)
        address_frame = ttk.LabelFrame(info_frame, text="Address")
        address_frame.pack(fill="x", padx=5, pady=5)
        birth_date_frame = ttk.LabelFrame(info_frame, text="Birth date")
        birth_date_frame.pack(fill="x", padx=5, pady=5)
        occupation_frame = ttk.LabelFrame(info_frame, text="Occupation")
        occupation_frame.pack(fill="x", padx=5, pady=5)
        notes_frame = ttk.LabelFrame(info_frame, text="Notes")
        notes_frame.pack(fill="x", padx=5, pady=5)

        # ===== text fields =====
        self.name_text = ContactTextWidget(name_frame, font=text_font,
                                           text=self.contact.name)
        self.name_text.pack(fill="x", padx=10, pady=5)

        self.email_text = ContactTextWidget(email_frame, font=text_font,
                                            text=self.contact.email)
        self.email_text.pack(fill="x", padx=10, pady=5)

        self.phone_text = ContactTextWidget(phone_frame, font=text_font,
                                            text=self.contact.phone)
        self.phone_text.pack(fill="x", padx=10, pady=5)

        self.address_text = ContactTextWidget(address_frame, font=text_font,
                                              text=self.contact.address)
        self.address_text.pack(fill="x", padx=10, pady=5)

        self.birth_date_text = ContactTextWidget(birth_date_frame, font=text_font,
                                                 text=self.contact.birth_date)
        self.birth_date_text.pack(fill="x", padx=10, pady=5)

        self.occupation_text = ContactTextWidget(occupation_frame, font=text_font,
                                                 text=self.contact.occupation)
        self.occupation_text.pack(fill="x", padx=10, pady=5)

        self.notes_text = ContactTextWidget(notes_frame, font=text_font, height=7,
                                            text=self.contact.notes)
        self.notes_text.pack(fill="x", padx=10, pady=5)

        # Bind widgets with functions
        self.bind_class("Text", "<Tab>", self._focus_next_widget)
        self.bind_class("TButton", "<Return>", lambda event: event.widget.invoke())
        self.search_field.bind("<<ComboboxSelected>>", self._on_contact_select)
        self.edit_button.focus()

    def _on_contact_select(self, event):
        self.contact.get_contact(self.search_field.get())

        self._change_state("normal")

        self._reset_fields()

        self._draw_photo()
        self.name_text.insert("end", self.contact.name)
        self.email_text.insert("end", self.contact.email)  
        self.phone_text.insert("end", self.contact.phone)
        self.address_text.insert("end", self.contact.address)
        self.birth_date_text.insert("end", self.contact.birth_date)
        self.occupation_text.insert("end", self.contact.occupation)
        self.notes_text.insert("end", self.contact.notes)

        self._center_text(self.name_text)
        self._center_text(self.email_text)
        self._center_text(self.phone_text)
        self._center_text(self.address_text)
        self._center_text(self.birth_date_text)
        self._center_text(self.occupation_text)
        self._center_text(self.notes_text)

        self.edit_button.configure(state="normal")
        self._change_state("disabled")

    def _confirm_popup(self):
        self.popup = ConfirmPopUp(self.frame, text="Are you sure you want to commit?")
        self._change_state("disabled", confirm_popup=True)
        self.frame.wait_window(self.popup.top)
        self._change_state("normal", confirm_popup=True)

        if self.popup.result:
            return True

    def _apply_changes(self):
        if self._confirm_popup():
            loaded_name = self.contact.name

            try:
                self.contact.photo = convert_to_binary(self.photo_path_text.get("1.0", "end").rstrip())
            except FileNotFoundError:
                if self.photo_path_text.get("1.0", "end").rstrip() != "":
                    print("FileNotFoundError")

            self.contact.name = self.name_text.get("1.0", "end").rstrip()
            self.contact.email = self.email_text.get("1.0", "end").rstrip()
            self.contact.phone = self.phone_text.get("1.0", "end").rstrip()
            self.contact.address = self.address_text.get("1.0", "end").rstrip()
            self.contact.birth_date = self.birth_date_text.get("1.0", "end").rstrip()
            self.contact.occupation = self.occupation_text.get("1.0", "end").rstrip()
            self.contact.notes = self.notes_text.get("1.0", "end").rstrip()

            self.contact.update_contact(loaded_name)
            self._exit_edit_mode()

    def _enter_edit_mode(self):
        self._change_state("normal")

        # ----- Photo -----
        if self.photo_label is not None:
            self.photo_label.destroy()

        self._draw_photo_browser()
        # ----- Photo END -----

        self.edit_button.destroy()
        self.apply_button = ttk.Button(self.buttons_container, text="Apply", width=10,
                                       command=self._apply_changes)
        self.apply_button.pack(side="left", padx=5, pady=10)

        self.cancel_button = ttk.Button(self.buttons_container, text="Cancel", width=10,
                                        command=self._exit_edit_mode)
        self.cancel_button.pack(side="right", padx=5, pady=10)

    def _exit_edit_mode(self):
        self._change_state("disabled")

        self.apply_button.destroy()
        self.cancel_button.destroy()
        self.photo_frame.destroy()

        self.edit_button = ttk.Button(self.buttons_container, text="Edit", width=10,
                                      command=self._enter_edit_mode)
        self.edit_button.pack(padx=5, pady=10)

        self._on_contact_select("required_but_unimportant_param") # ----- Retrieve and refill fields -----

    def _change_state(self, state, confirm_popup=False):
        self.name_text.configure(state=state)
        self.email_text.configure(state=state)
        self.phone_text.configure(state=state)
        self.address_text.configure(state=state)
        self.birth_date_text.configure(state=state)
        self.occupation_text.configure(state=state)
        self.notes_text.configure(state=state)

        if confirm_popup:
            self.apply_button.configure(state=state)
            self.cancel_button.configure(state=state)
            self.photo_path_text.configure(state=state)
            self.browse_button.configure(state=state)

    def _browse_file(self):
        file_name = tk.filedialog.askopenfilename(initialdir="/", title="Select image",
                                                  filetypes=(
                                                      ('Image files', ('*.png', '*.jpg', '*.gif', '*.jpeg')),
                                                      ('All files', '*.*')
                                                  ))

        self.photo_path_text.delete("1.0", "end")  # Make sure the text field is empty before inserting text
        self.photo_path_text.insert("end", file_name)

    def _draw_photo(self):
        if self.contact.photo is not None:  # Only draws the photo if there is actually a photo to draw
            # ===== Load Image =====
            img = Image.open(io.BytesIO(self.contact.photo))

            init_width, init_height = img.size
            img_width, img_height = set_img_size(init_width, init_height)

            # ===== Profile Photo =====
            photo = ImageTk.PhotoImage(img.resize((img_width, img_height)))
            self.photo_label = tk.Label(self.frame.interior, image=photo, bg=bg_color)
            self.photo_label.image = photo  # Keep a reference so tkinter garbage collector doesn't blanc out the image
            self.photo_label.pack(padx=5, pady=5)

    def _draw_photo_browser(self):
        self.photo_frame = ttk.LabelFrame(self.frame.interior, text="Image")
        self.photo_frame.pack(side="top", padx=5, pady=5)

        self.browse_button = ttk.Button(self.photo_frame, text="Browse", width=10,
                                        command=self._browse_file)
        self.browse_button.pack(side="right", padx=5, pady=5)

        self.photo_path_text = tk.Text(self.photo_frame, width=109, height=2, wrap="word", borderwidth=0,
                                       font=text_font)
        self.photo_path_text.pack(side="left", padx=5, pady=5)
        self.photo_path_text.tag_add("center", "1.0", "end")
        self.photo_path_text.tag_config("center", justify=tk.CENTER)

    def _on_close(self):
        self.contact.close_connection()
        self.destroy()

    def _reset_fields(self):
        if self.photo_label:
            self.photo_label.destroy()
        self.name_text.delete("1.0", "end")
        self.email_text.delete("1.0", "end")
        self.phone_text.delete("1.0", "end")
        self.address_text.delete("1.0", "end")
        self.birth_date_text.delete("1.0", "end")
        self.occupation_text.delete("1.0", "end")
        self.notes_text.delete("1.0", "end")

    @staticmethod
    def _focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return "break"

    @staticmethod
    def _center_text(text_field):
        text_field.tag_add("center", "1.0", "end")
        text_field.tag_config("center", justify=tk.CENTER)


class AddContactApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        self.root = super().__init__(*args, **kwargs)
        self.state("zoomed")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.frame = VerticalScrolledFrame(self.root)
        # The height is set manually here
        canvas_height = self.winfo_screenheight()
        self.frame.canvas.config(height=canvas_height)
        self.frame.pack(fill="x")

        self.popup = None
        self.apply_button = None
        self.cancel_button = None

        # Creating a contact object which can communicate with database
        self.contact = ContactsContainer()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        style = ttk.Style()
        style.configure(".", font=text_font, background=bg_color)

        # ===== Load Image =====
        self.photo_frame = ttk.LabelFrame(self.frame.interior, text="Image")
        self.photo_frame.pack(side="top", padx=5, pady=5)

        self.file_explorer_button = ttk.Button(self.photo_frame, text="Browse", width=10,
                                               command=self._browse_file)
        self.file_explorer_button.pack(side="right", padx=5, pady=5)

        self.photo_path_text = tk.Text(self.photo_frame, width=109, height=2, wrap="word", borderwidth=0,
                                       font=text_font)
        self.photo_path_text.pack(side="left", padx=5, pady=5)
        self.photo_path_text.tag_add("center", "1.0", "end")
        self.photo_path_text.tag_config("center", justify=tk.CENTER)

        # ===== Buttons =====
        self.buttons_container = tk.Frame(self.frame.interior, bg=bg_color)
        self.buttons_container.pack(side="bottom", padx=5)

        self.apply_button = ttk.Button(self.buttons_container, text="Apply", width=10,
                                       command=self._apply_changes)
        self.apply_button.pack(side="left", padx=5, pady=10)

        self.cancel_button = ttk.Button(self.buttons_container, text="Cancel", width=10,
                                        command=self._cancel_edit)
        self.cancel_button.pack(side="right", padx=5, pady=10)

        # ===== info frame =====
        info_frame = tk.Frame(self.frame.interior, bg=bg_color)
        info_frame.pack(side="bottom")

        name_frame = ttk.LabelFrame(info_frame, text="Name")
        name_frame.pack(fill="x", padx=5, pady=5)
        email_frame = ttk.LabelFrame(info_frame, text="Email")
        email_frame.pack(fill="x", padx=5, pady=5)
        phone_frame = ttk.LabelFrame(info_frame, text="Phone number")
        phone_frame.pack(fill="x", padx=5, pady=5)
        address_frame = ttk.LabelFrame(info_frame, text="Address")
        address_frame.pack(fill="x", padx=5, pady=5)
        birth_date_frame = ttk.LabelFrame(info_frame, text="Birth date")
        birth_date_frame.pack(fill="x", padx=5, pady=5)
        occupation_frame = ttk.LabelFrame(info_frame, text="Occupation")
        occupation_frame.pack(fill="x", padx=5, pady=5)
        notes_frame = ttk.LabelFrame(info_frame, text="Notes")
        notes_frame.pack(fill="x", padx=5, pady=5)
        # ===== text fields =====
        self.name_text = ContactTextWidget(name_frame, font=text_font, text="")
        self.name_text.pack(padx=10, pady=5)

        self.email_text = ContactTextWidget(email_frame, font=text_font, text="")
        self.email_text.pack(padx=10, pady=5)

        self.phone_text = ContactTextWidget(phone_frame, font=text_font, text="")
        self.phone_text.pack(padx=10, pady=5)

        self.address_text = ContactTextWidget(address_frame, font=text_font, text="")
        self.address_text.pack(padx=10, pady=5)
        self.birth_date_text = ContactTextWidget(birth_date_frame, font=text_font, text="")
        self.birth_date_text.pack(padx=10, pady=5)

        self.occupation_text = ContactTextWidget(occupation_frame, font=text_font, text="")
        self.occupation_text.pack(padx=10, pady=5)

        self.notes_text = ContactTextWidget(notes_frame, font=text_font, height=7, text="")
        self.notes_text.pack(padx=10, pady=5)

        self._change_text_state("normal")
        self.bind_class("Text", "<Tab>", self._focus_next_widget)
        self.bind_class("TButton", "<Return>", lambda event: event.widget.invoke())
        self.file_explorer_button.focus()

    def on_close(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
        self.contact.close_connection()

    def _confirm_popup(self, message):
        self._change_text_state("disabled")

        self.popup = ConfirmPopUp(self.frame, text=message)
        self.apply_button["state"] = "disabled"
        self.cancel_button["state"] = "disabled"
        self.frame.wait_window(self.popup.top)
        self.apply_button["state"] = "normal"
        self.cancel_button["state"] = "normal"

        self._change_text_state("normal")

        if self.popup.result:
            return True

    def _change_text_state(self, state):
        self.name_text.configure(state=state)
        self.email_text.configure(state=state)
        self.phone_text.configure(state=state)
        self.address_text.configure(state=state)
        self.birth_date_text.configure(state=state)
        self.occupation_text.configure(state=state)
        self.notes_text.configure(state=state)

    def _apply_changes(self):
        if self._confirm_popup("Are you sure you want to commit and add the contact?"):
            if self.photo_path_text.get("1.0", "end").rstrip() != "":
                print(self.photo_path_text.get("1.0", "end").rstrip())
                self.contact.photo = convert_to_binary(self.photo_path_text.get("1.0", "end").rstrip())
            self.contact.name = self.name_text.get("1.0", "end").rstrip()
            self.contact.email = self.email_text.get("1.0", "end").rstrip()
            self.contact.phone = self.phone_text.get("1.0", "end").rstrip()
            self.contact.address = self.address_text.get("1.0", "end").rstrip()
            self.contact.birth_date = self.birth_date_text.get("1.0", "end").rstrip()
            self.contact.occupation = self.occupation_text.get("1.0", "end").rstrip()
            self.contact.notes = self.notes_text.get("1.0", "end").rstrip()

            self.contact.create_contact()
            self._reset_textfields()

    def _cancel_edit(self):
        if self._confirm_popup("Are you sure you want to cancel and reset textfields?"):
            self._reset_textfields()

    def _reset_textfields(self):
        self.photo_path_text.delete("1.0", "end")
        self.name_text.delete("1.0", "end")
        self.email_text.delete("1.0", "end")
        self.phone_text.delete("1.0", "end")
        self.address_text.delete("1.0", "end")
        self.birth_date_text.delete("1.0", "end")
        self.occupation_text.delete("1.0", "end")
        self.notes_text.delete("1.0", "end")

    def _browse_file(self):
        file_name = tk.filedialog.askopenfilename(initialdir="/", title="Select image",
                                                  filetypes=(
                                                      ('Image files', ('*.png', '*.jpg', '*.gif', '*.jpeg', '*.jfif')),
                                                      ('All files', '*.*')
                                                  ))

        self.photo_path_text.delete("1.0", "end")  # Make sure the text field is empty before inserting text
        self.photo_path_text.insert("end", file_name)

    def _on_close(self):
        self.contact.close_connection()
        self.destroy()

    @staticmethod
    def _focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return "break"


if __name__ == "__main__":

    app = DisplayAndEdit()
    app.state("zoomed")  # Open maximized
    # print(app.cget("bg"))
    # app.protocol("WM_DELETE_WINDOW", app.contact.close_connection())  # TODO: Y this not work
    app.mainloop()
