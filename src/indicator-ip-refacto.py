import os
import signal
import gi
from src.indicator_ip.net_utils import NetUtils

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, Gdk


class IndicatorIPMenu(object):

    def __init__(self) -> None:
        super().__init__()

        icon = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'indicator_ip', 'images', 'ip_white.png')
        print(icon)

        self.app_id = 'ip-indicator'

        self.indicator = AppIndicator3.Indicator.new(self.app_id,
                                                     icon,
                                                     AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        # prepare the clipboard to receive copied IPs
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        self.refresh(None)

    def create_menu(self):
        menu = Gtk.Menu()

        # manual refresh
        item_refresh = Gtk.MenuItem(label='Refresh')
        item_refresh.connect('activate', self.refresh)
        menu.append(item_refresh)

        # separator
        sep = Gtk.SeparatorMenuItem()
        sep.show()
        menu.append(sep)

        # get all interface
        group = None
        for interface in NetUtils.get_all_interface():
            new_radio = Gtk.RadioMenuItem.new_with_label_from_widget(label=str(interface), group=group)
            new_radio.connect("activate", self.on_clicked_item, interface)
            new_radio.show()
            if group is None:
                group = new_radio.get_group()[0]
            menu.append(new_radio)

        # separator
        sep = Gtk.SeparatorMenuItem()
        sep.show()
        menu.append(sep)

        # quit item
        item_quit = Gtk.MenuItem(label='Quit')
        item_quit.connect('activate', self.quit)
        menu.append(item_quit)

        menu.show_all()
        return menu

    @staticmethod
    def quit(_):
        Gtk.main_quit()

    def refresh(self, _):
        print("refresh")
        self.indicator.set_menu(self.create_menu())
        # set by default the public IP as label
        self.indicator.set_label(str(NetUtils.get_public_interface().ip),
                                 str(NetUtils.get_public_interface().ip))

    def on_clicked_item(self, _, interface):
        # copy to clipboard the ip
        self.clipboard.set_text(interface.ip, -1)
        print("'%s' copied to clipboard" % interface.ip)
        # update the label so we see the selected ip
        self.indicator.set_label(str(interface.ip), str(interface.ip))


def main():
    IndicatorIPMenu()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gtk.main()


if __name__ == "__main__":
    main()
