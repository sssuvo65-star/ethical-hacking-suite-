from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
import socket
import json
import urllib.request
from threading import Thread


class MultiSecurityToolUI(BoxLayout):

  def __init__(self, **kwargs):
    super().__init__(orientation="vertical", padding=12, spacing=8, **kwargs)

    # Title Banner
    self.add_widget(
        Label(
            text="[b]ETHICAL HACKING SUITE[/b]",
            markup=True,
            font_size="22sp",
            size_hint_y=0.1,
            color=(0, 0.8, 1, 1),
        )
    )

    # Input Field
    self.target_input = TextInput(
        hint_text="Enter Domain / IP (e.g. scanme.nmap.org or google.com)",
        multiline=False,
        size_hint_y=0.1,
        font_size="15sp",
    )
    self.add_widget(self.target_input)

    # Action Buttons Area (Horizontal Layout)
    btn_layout = BoxLayout(
        orientation="horizontal", spacing=5, size_hint_y=0.12
    )

    self.btn_port = Button(
        text="1. Port Scan",
        background_color=(0, 0.5, 0.9, 1),
        font_size="13sp",
        bold=True,
    )
    self.btn_port.bind(on_press=self.start_port_scan)
    btn_layout.add_widget(self.btn_port)

    self.btn_ip_info = Button(
        text="2. IP Info",
        background_color=(0, 0.7, 0.5, 1),
        font_size="13sp",
        bold=True,
    )
    self.btn_ip_info.bind(on_press=self.start_ip_info)
    btn_layout.add_widget(self.btn_ip_info)

    self.btn_sub = Button(
        text="3. Admin Scan",
        background_color=(0.9, 0.4, 0.2, 1),
        font_size="13sp",
        bold=True,
    )
    self.btn_sub.bind(on_press=self.start_admin_scan)
    btn_layout.add_widget(self.btn_sub)

    self.add_widget(btn_layout)

    # Output Scroll Area
    self.scroll = ScrollView(size_hint_y=0.68)
    self.output_label = Label(
        text="Enter target domain above and select a tool to run.",
        size_hint_y=None,
        halign="left",
        valign="top",
        color=(0.9, 0.9, 0.9, 1),
        font_size="14sp",
    )
    self.output_label.bind(
        texture_size=lambda instance, value: setattr(instance, "height", value[1])
    )
    self.output_label.bind(
        width=lambda instance, value: setattr(
            instance, "text_size", (value, None)
        )
    )
    self.scroll.add_widget(self.output_label)
    self.add_widget(self.scroll)

  def get_target(self):
    target = self.target_input.text.strip()
    if not target:
      self.output_label.text = "[!] Error: Please enter a valid Target Domain or IP address!"
      return None
    return target

  # --- Tool 1: Port Scanner ---
  def start_port_scan(self, instance):
    target = self.get_target()
    if target:
      self.output_label.text = f"Running Port Scan on {target}...\n\n"
      Thread(target=self.run_port_scan, args=(target,), daemon=True).start()

  def run_port_scan(self, target):
    try:
      ip = socket.gethostbyname(target)
      self.output_label.text += f"Target IP: {ip}\n"
      self.output_label.text += "=" * 38 + "\n"
      ports = [21, 22, 53, 80, 443, 8080, 3306]

      for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.2)
        res = s.connect_ex((ip, port))
        if res == 0:
          self.output_label.text += f"[+] Port {port:<5}: OPEN\n"
        else:
          self.output_label.text += f"[-] Port {port:<5}: Closed\n"
        s.close()
      self.output_label.text += "\n[✔] Port Scan Completed!"
    except Exception as e:
      self.output_label.text += f"\n[!] Error: {str(e)}"

  # --- Tool 2: IP Info / Geolocation ---
  def start_ip_info(self, instance):
    target = self.get_target()
    if target:
      self.output_label.text = f"Fetching IP & Geolocation info for {target}...\n\n"
      Thread(target=self.run_ip_info, args=(target,), daemon=True).start()

  def run_ip_info(self, target):
    try:
      ip = socket.gethostbyname(target)
      url = f"http://ip-api.com/json/{ip}"
      req = urllib.request.urlopen(url)
      data = json.loads(req.read().decode())

      if data.get("status") == "success":
        self.output_label.text += f"Target IP  : {data.get('query')}\n"
        self.output_label.text += f"Country    : {data.get('country')}\n"
        self.output_label.text += f"Region/City: {data.get('city')}, {data.get('regionName')}\n"
        self.output_label.text += f"ISP        : {data.get('isp')}\n"
        self.output_label.text += f"Organization: {data.get('org')}\n"
        self.output_label.text += f"ZIP Code   : {data.get('zip')}\n"
      else:
        self.output_label.text += "[!] Failed to retrieve IP information."
      self.output_label.text += "\n[✔] Info Lookup Completed!"
    except Exception as e:
      self.output_label.text += f"\n[!] Error: {str(e)}"

  # --- Tool 3: Admin Panel Scanner ---
  def start_admin_scan(self, instance):
    target = self.get_target()
    if target:
      self.output_label.text = f"Scanning common Admin pages on {target}...\n\n"
      Thread(target=self.run_admin_scan, args=(target,), daemon=True).start()

  def run_admin_scan(self, target):
    try:
      if not target.startswith("http"):
        target_url = "http://" + target

      admin_paths = [
          "/admin",
          "/admin/",
          "/login",
          "/admin.php",
          "/wp-admin",
          "/administrator",
      ]
      found = False

      for path in admin_paths:
        full_url = target_url + path
        try:
          req = urllib.request.Request(
              full_url, headers={"User-Agent": "Mozilla/5.0"}
          )
          response = urllib.request.urlopen(req, timeout=2.5)
          code = response.getcode()
          if code == 200:
            self.output_label.text += f"[+] FOUND: {full_url} (HTTP {code})\n"
            found = True
        except Exception:
          self.output_label.text += f"[-] Not Found: {path}\n"

      if not found:
        self.output_label.text += "\n[-] No common admin pages found."
      self.output_label.text += "\n[✔] Admin Page Scan Completed!"
    except Exception as e:
      self.output_label.text += f"\n[!] Error: {str(e)}"


class MultiSecurityApp(App):

  def build(self):
    self.title = "Ethical Hacking Suite"
    return MultiSecurityToolUI()


if __name__ == "__main__":
  MultiSecurityApp().run()



