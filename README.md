# TMD – Telegram Message Deleter (Systematic)

**TMD** (Telegram Message Deleter) is a **systematic automation tool** designed to help you **delete messages in bulk from Telegram groups** using the web version ([web.telegram.org/k/](https://web.telegram.org/k/)).  
It works by leveraging Telegram’s search function to find all messages you want to remove. Then, it automatically:

- Scrolls to each message.
- Right‑clicks and selects **Delete**.
- Confirms the deletion (with or without “Delete for all members”).
- Moves to the previous/next search result – **looping until all targeted messages are gone**.

The name **Systematic** reflects the ordered, retry‑based, step‑by‑step processing that ensures no message is accidentally skipped.

> ⚠️ **Disclaimer**: This tool automates user actions on a third‑party platform. Automated deletion of messages at scale may violate Telegram’s [Terms of Service](https://telegram.org/tos). Use responsibly and at your own risk. The author is not liable for any account restrictions, bans, or data loss.

---

## 📦 Download the Release

The latest release is packaged as **`main.zip`** and includes a standalone **Windows executable** (`TMD System.exe`) – no Python installation required.

1. **Download** `main.zip` from the [Releases page](https://github.com/TheRealMrDjango/TMD_systematic/releases/tag/v1.0.0).
2. **Extract** the ZIP file to a folder of your choice.
3. **Run** `main.exe` and follow the on‑screen instructions.

> 💡 **Pro tip**: Keep the `.exe` in a dedicated folder – it creates temporary files and logs in the same directory.

---

## 🧠 How It Works (Systematic Approach)

1. **Open** Telegram Web in a Firefox browser (this happens automatically).
2. **Manual login** – you log in and navigate to the desired group.
3. **Search** for the messages you want to delete by your own username.
4. The script then **systematically** processes each found message:
   - Scrolls it into view.
   - Right‑clicks on the message bubble.
   - Clicks **Delete** from the context menu (uses a strict XPath to avoid clicking other options).
   - Checks the **“Delete for all members”** checkbox if present (gracefully skips if not).
   - Clicks the final red **DELETE** button.
   - Clicks the **up arrow** (←) to go to the previous search result.
5. This loop continues until **all messages from your search are deleted** or you stop it with `Ctrl+C`.

---

## ✨ Features

- ✅ **Systematic loop** – processes every message in your search results in order.
- ✅ **Retry mechanism** – each message is attempted up to 2 times if the context menu fails.
- ✅ **Robust right‑click** – uses `ActionChains` + JavaScript fallback.
- ✅ **Precise Delete selection** – strict XPath for `.btn-menu-item.danger` with `span[text()='Delete']` – avoids “Translate” or other options.
- ✅ **Smart checkbox handling** – automatically skips “Delete for all members” when not available (messages older than 48h).
- ✅ **JavaScript‑powered final click** – bypasses UI overlays/ripple effects.
- ✅ **Automatic navigation** – uses the search bar’s up arrow to move to the previous message.

---

## 🛠️ Prerequisites

**For the executable (`main.zip`)**
- Windows 10 / 11
- Firefox browser installed

**For running from source code**
- Python 3.7+
- Firefox browser
- [Geckodriver](https://github.com/mozilla/geckodriver/releases) (Selenium can auto‑manage it)

---

## 📦 Installation (from source)

If you prefer to run the Python script directly:

```bash
git clone https://github.com/yourusername/tmd-systematic.git
cd tmd-systematic
python -m venv venv
source venv/bin/activate   # or `venv\Scripts\activate` on Windows
pip install selenium
