from kivy.uix.filechooser import FileChooserIconView, FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.button import Button
from pathlib import Path

from src.services.storage_service import SettingsStore


class FileChooserHelper:

    @staticmethod
    def show_dir_chooser(initial_path, on_choose):
        FileChooserHelper._show_chooser(
            title="Select Source Directory",
            initial_path=initial_path,
            on_choose=on_choose,
            dirselect=True,
            filter_dirs_only=True,
        )

    @staticmethod
    def show_file_chooser(initial_path, target_filename, on_choose, selected_path=None):
        import os as _os

        def file_filter(folder, filename):
            full = _os.path.join(folder, filename)
            return _os.path.isdir(full) or _os.path.basename(full).lower() == target_filename.lower()

        FileChooserHelper._show_chooser(
            title=f"Select {target_filename}",
            initial_path=initial_path,
            on_choose=on_choose,
            dirselect=False,
            custom_filter=file_filter,
            selected_path=selected_path,
        )

    @staticmethod
    def _show_chooser(title, initial_path, on_choose, dirselect=True,
                      filter_dirs_only=False, custom_filter=None, selected_path=None):
        import os as _os

        current_path = selected_path if selected_path else (initial_path if initial_path else "")

        if filter_dirs_only:
            def _dirs_only(folder, filename):
                return _os.path.isdir(_os.path.join(folder, filename))
            file_filter = _dirs_only
        else:
            file_filter = custom_filter

        saved_view = SettingsStore.load().get("filechooser_view", "icon")

        icon_view = FileChooserIconView(
            dirselect=dirselect, path=initial_path, filters=[file_filter]
        )
        list_view = FileChooserListView(
            dirselect=dirselect, path=initial_path, filters=[file_filter]
        )

        chosen = {"path": current_path}

        label_text = f"Selected: {current_path}" if current_path else "Selected: (none)"
        path_label = Label(
            text=label_text, size_hint_y=None, height='28dp', halign="left"
        )
        path_label.bind(
            size=lambda *_: setattr(path_label, "text_size", (path_label.width, None))
        )

        def update_path_label(instance, selection):
            if selection:
                chosen["path"] = selection[0]
                path_label.text = f"Selected: {selection[0]}"

        icon_view.bind(selection=update_path_label)
        list_view.bind(selection=update_path_label)

        def confirm(*_):
            if chosen["path"]:
                on_choose(chosen["path"])
            popup.dismiss()

        def cancel(*_):
            popup.dismiss()

        view_container = BoxLayout()
        current_view = saved_view
        if current_view == "list":
            view_container.add_widget(list_view)
        else:
            view_container.add_widget(icon_view)

        def toggle_view(btn):
            nonlocal current_view
            view_container.clear_widgets()
            if current_view == "icon":
                view_container.add_widget(list_view)
                current_view = "list"
                btn.text = "Icon View"
            else:
                view_container.add_widget(icon_view)
                current_view = "icon"
                btn.text = "List View"
            SettingsStore.save({"filechooser_view": current_view})

        is_list = saved_view == "list"
        toggle_btn = ToggleButton(
            text="Icon View" if is_list else "List View",
            size_hint=(None, None),
            size=('100dp', '28dp'),
        )
        toggle_btn.bind(on_release=toggle_view)

        top_bar = BoxLayout(size_hint_y=None, height='32dp')
        top_bar.add_widget(path_label)
        top_bar.add_widget(toggle_btn)

        btn_row = BoxLayout(size_hint_y=None, height='44dp', spacing='10dp', padding=[dp(0), dp(6)])
        btn_row.add_widget(Button(text="Cancel", on_release=cancel))
        choose_btn = Button(
            text="Choose", background_color=(0.2, 0.6, 0.2, 1), on_release=confirm
        )
        btn_row.add_widget(choose_btn)

        content = BoxLayout(orientation="vertical")
        content.add_widget(top_bar)
        content.add_widget(view_container)
        content.add_widget(btn_row)

        popup = Popup(title=title, content=content, size_hint=(0.8, 0.85))
        popup.open()
