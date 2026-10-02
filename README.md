# Angel Studios

**Gymnastics & Performance Studio**  
Piazza, Addis Ababa, Ethiopia — behind Merkato Market

A complete website and class-booking system. Ballet · Bar Dancing · Tightwire ·
Flipping / Gymnastics · **5,000 ETB per month** · maximum 25 students per class ·
payment in cash, in person · English and አማርኛ.

---

## Run it — one click

1. Open this folder.
2. Double-click **`START-HERE.bat`**.
3. Your browser opens at **http://127.0.0.1:8000**

Keep the black window open while you use the site. Close it to stop.

> **Python is required.** If the window says Python was not found, install it
> free from <https://www.python.org/downloads/> and tick **"Add Python to PATH"**
> during installation. Nothing else needs installing — no Node, no pip packages.

---

## Send a link to your manager or students

Double-click **`SHARE-ONLINE.bat`**.

It starts the site *and* creates a public web address you can send to anyone,
on any device, anywhere — no Wi-Fi needed. The address appears on screen and is
saved to your Desktop as `Angel-Studios-LINK.txt`.

> The computer must stay switched on with that window open for the link to keep
> working. It is ideal for a review or a demo. For a permanent address that
> never expires, see `deploy/PYTHONANYWHERE.md`.

---

## Sign in

| Role | Email | Password |
| --- | --- | --- |
| **Administrator** | `admin@angelstudios.et` | `AngelAdmin#2026` |
| **Student** (demo) | `sarah@example.com` | `Student#2026` |

**Change the administrator password before real use:**
*My Account → Profile → Change password*.

Visitors can also create their own account from the **Register** page.

---

## What the site includes

**Public pages**
Home · About · Classes (plus a page per class) · Schedule · Pricing · Contact ·
Register · Login

**Student dashboard** (`My Account`)
Upcoming classes, booking history with cancellation, live schedule, profile,
password change.

**Admin dashboard** (`Admin`)
Overview statistics and charts · full class management · the monthly schedule ·
bookings · customers and their history · website enquiries · studio settings.

**Two languages**
The **EN | አማ** button in the top bar switches the whole site between English
and Amharic.

---

## Setting up the real schedule

The site ships with **sample** class times so the booking system can be
demonstrated. Every one is marked **PLACEHOLDER**.

1. Sign in as the administrator.
2. Open **Admin → Schedule**.
3. Use **Add session**, **Edit** and **Delete** to enter the studio's real days
   and times.
4. Untick *placeholder session* on each confirmed row to remove the badge.

---

## Replacing the placeholder details

Sign in as the administrator, open **Admin → Settings**, and replace:

* phone number
* email address
* opening hours
* social media links
* the Google Maps search term

Also worth doing:

* **Photos** — put real images in `public/assets/img/` and set the `image` field
  per class in **Admin → Classes** (for example `assets/img/ballet.jpg`).
* **Coaches** — set the instructor name per session in **Admin → Schedule**.
* **Logo** — replace `public/assets/img/logo-mark.svg`.

---

## Back up your data

Everything the studio owns — accounts, bookings, the schedule — lives in one
file:

```
data/angel_studios.sqlite3
```

**Copy it somewhere safe every week.** That single file is your entire database.
Restoring it is just putting it back.

---

## Folder contents

| Path | What it is |
| --- | --- |
| `START-HERE.bat` | Run the website on this computer |
| `SHARE-ONLINE.bat` | Run it and create a public link |
| `server.py` | The program that starts the site |
| `wsgi.py` | Entry point for web hosting |
| `app/` | The backend: database, security, API |
| `public/` | The website itself (pages, styles, images) |
| `data/` | Your database lives here |
| `deploy/PYTHONANYWHERE.md` | Guide: get a permanent public address |
| `tools/` | Maintenance scripts |
| `README.md` | This file |

---

## Common questions

**The window closes immediately.**  
Python is not installed, or was not added to PATH. Reinstall it and tick
*"Add Python to PATH"*.

**"Port 8000 is already in use."**  
The site is already running in another window. Close it, or run:
`py server.py --port 8001`

**The public link stopped working.**  
Free links expire and the address changes. Close the window and run
`SHARE-ONLINE.bat` again to get a new one. For a permanent link, follow
`deploy/PYTHONANYWHERE.md`.

**The class times are not the real ones.**  
Correct — they are clearly marked as samples. Set the real ones in
*Admin → Schedule*.

**Can customers pay online?**  
No. Payment is **cash only, in person at the studio**. That is intentional by
design and stated on the site.

**How do customers change a class time?**  
Rescheduling is done **in person at the studio**, as the studio requested. The
site says this on every relevant page.

---

© Angel Studios · Piazza, Addis Ababa, Ethiopia — behind Merkato Market
