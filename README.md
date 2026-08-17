# 🕌 Islamic Prayer Hub for Home Assistant 🕋

Prayer Hub is a Home Assistant custom integration that turns a wall-mounted Fully Kiosk tablet into a prayer-time display while coordinating your TV and selected lights.

It uses **London Unified Prayer Times (LUPT)** as its timetable source.


> [!NOTE]
> ## 🧭 Project status — stable community release
>
> Prayer Hub was originally created for a personal Home Assistant setup and is being shared so others can use or adapt it.
>
> **This project is provided as-is and should not be considered actively maintained.** There is no planned release schedule and compatibility fixes are not guaranteed after future Home Assistant, HACS, LUPT, Fully Kiosk, browser/WebView or YouTube changes.
>
> The current release represents a known-working version at the time it was published. You are welcome to fork the repository, adapt it for your own setup, or submit community fixes.
>
> Prayer Hub is intentionally **not intended for submission to the default HACS catalogue** at this stage. Users can install it either as a **HACS custom repository** or manually.

At prayer time Prayer Hub can:

- 🕌 detect Fajr, Dhuhr/Zuhr, Asr, Maghrib and Isha from LUPT;
- 📺 mute a configured TV and restore its previous mute state afterwards;
- 💡 pulse only lights that were already on;
- 🎚️ restore each light's previous brightness and active colour mode;
- 📱 wake a Fully Kiosk tablet;
- 🎨 show a prayer-specific landscape theme;
- 🌙 display the prayer name in English and Arabic;
- 📅 display the Islamic date from LUPT;
- 📖 rotate locally bundled Qur'an reminders and Qur'anic du'a;
- 🔊 play a YouTube adhan full-screen;
- 🌅 use a separate Fajr adhan video;
- ↩️ return the tablet to your chosen Home Assistant dashboard;
- 📡 expose sensors for current prayer, next prayer, next prayer time, countdown, Islamic date and last Prayer Hub run.

> [!IMPORTANT]
> Prayer Hub is a community custom integration, not an official Home Assistant integration. Test it before relying on it.

## 📋 Requirements

Prayer Hub currently expects:

1. **Home Assistant**
2. **London Unified Prayer Times (LUPT)** custom integration
3. **Fully Kiosk Browser** integrated with Home Assistant
4. A Home Assistant `media_player` entity if you want TV muting
5. One or more Home Assistant `light` entities if you want the light-pulse notification
6. Internet access from the tablet for the embedded YouTube adhan

The TV and lights are configured during setup; use the entities appropriate to your own home.

## 🕰️ Prayer-time source: LUPT

Prayer Hub currently uses the `homeassistant-lupt` custom integration:

`https://github.com/sshaikh/homeassistant-lupt`

Install and configure LUPT before adding Prayer Hub.

For the East London Mosque / London Unified Prayer Timetable source, LUPT users commonly configure the East London Mosque prayer timetable page:

`https://www.eastlondonmosque.org.uk/prayers`

LUPT stores prayer timestamps as timezone-aware values. Prayer Hub converts scheduled timestamps using Home Assistant's local timezone, so British Summer Time / Greenwich Mean Time changes are handled automatically when Home Assistant is configured for `Europe/London`.

### 🌤️ Asr selection

LUPT offers both Asr methods:

- **Mithl 1** — earlier Asr
- **Mithl 2** — later/Hanafi Asr

Choose the method that matches the timetable you intend to follow.

## 📦 Installation

### 🛍️ Option A — HACS custom repository

This is the easiest method once this repository is public on GitHub.

1. Install HACS if you do not already use it.
2. Open **HACS**.
3. Open the three-dot menu.
4. Select **Custom repositories**.
5. Paste this repository URL:

   `https://github.com/ebrahimflows/HA_islamic_prayer_hub`

6. Choose **Integration**.
7. Select **Add**.
8. Find **Prayer Hub** in HACS and download it.
9. Restart Home Assistant.
10. Go to **Settings → Devices & services → Add integration**.
11. Search for **Prayer Hub**.

HACS installs integrations into Home Assistant's `custom_components` directory.

### 📁 Option B — Manual installation

1. Download the latest GitHub release ZIP.
2. Extract it.
3. Copy:

   `custom_components/prayer_hub`

   into:

   `/config/custom_components/prayer_hub`

   On Home Assistant OS/File Editor this may appear as:

   `/homeassistant/custom_components/prayer_hub`

4. Confirm this file exists:

   `/config/custom_components/prayer_hub/manifest.json`

5. Restart Home Assistant.
6. Go to **Settings → Devices & services → Add integration → Prayer Hub**.

## ⚙️ Prayer Hub setup

During setup Prayer Hub asks for:

### 🕌 London Unified Prayer Times entity

Prayer Hub detects LUPT entities automatically. A typical entity is:

`lupt.lupt`

### 📺 TV media player

Choose the TV/media-player entity you want Prayer Hub to mute during the adhan.

Example:

`media_player.living_room_tv`

### 📱 Fire tablet screen switch

Choose the Fully Kiosk screen switch for your tablet.

Example:

`switch.wall_tablet_screen`

### 🪪 Fully Kiosk device ID

Prayer Hub uses Fully Kiosk's `load_url` action.

To find the device ID:

1. Open **Developer Tools → Actions**.
2. Select **Fully Kiosk Browser: Load URL**.
3. Select your tablet.
4. Switch the action editor to YAML mode.
5. Copy the generated `device_id`.

### 🏠 Home Assistant base URL

Use a URL the tablet itself can reach.

Examples:

`http://homeassistant.local:8123`

or

`https://ha.example.com`

Prayer Hub attempts to prefill Home Assistant's configured internal or external URL where available.

### ↩️ Dashboard return path

This is where the tablet returns after the adhan.

Examples:

`/`

`/lovelace/0`

`/dashboard-tablet/home`

### 💡 Lights allowed to pulse

Select **individual lights**, not helper groups, where possible.

Prayer Hub records only selected lights that are already on, pulses those lights twice, then restores their previous brightness and active colour mode.

Lights that were off are left off.

### 🔊 Regular adhan YouTube video ID

Default:

`SI4CScs4D2Q`

This is used for Dhuhr, Asr, Maghrib and Isha.

### 🌅 Fajr adhan YouTube video ID

Default:

`Yazp1Nz-eBE`

Fajr can use a different adhan. If no Fajr-specific video is configured, Prayer Hub falls back to the regular video.

### 🔉 Volume

YouTube player volume from 0 to 100.

Default: `85`

### ⏳ Countdown

Seconds shown before playback begins.

Default: `3`

### 🛟 Safety return timeout

If the YouTube player never reports that playback ended, the tablet returns after this timeout.

Default: `420` seconds.

## 🧪 First test

After setup, open **Developer Tools → Actions** and run:

```yaml
action: prayer_hub.start
data:
  prayer_name: Test
  prayer_time: "19:30"
```

Check that:

- your TV mutes if it was on;
- only selected lights that were already on pulse;
- those lights return to their previous settings;
- the tablet wakes;
- Prayer Hub opens;
- the video plays;
- the tablet returns to your dashboard;
- the TV's previous mute state is restored.

To restore the TV immediately while testing:

```yaml
action: prayer_hub.stop
```

## 🤖 Automatic operation

When automatic operation is enabled, Prayer Hub watches the LUPT state.

Prayer Hub starts when LUPT enters:

- Fajr
- Zuhr
- Asr
- Maghrib
- Ishā / Isha

It ignores other LUPT periods such as Duha and Zawaal.

For automatic runs, the prayer time displayed on the tablet comes from the scheduled LUPT timestamp converted to Home Assistant local time rather than simply using the moment the event was detected.

## 📡 Sensors

Prayer Hub creates sensors similar to:

- `sensor.prayer_hub_current_prayer`
- `sensor.prayer_hub_next_prayer`
- `sensor.prayer_hub_next_prayer_time`
- `sensor.prayer_hub_next_prayer_countdown`
- `sensor.prayer_hub_islamic_date`
- `sensor.prayer_hub_last_prayer_mode`

Home Assistant may add a suffix if an entity with the same ID already exists.

## 🖥️ Dashboard examples

### 🏠 Built-in Home Assistant card

A ready-to-copy example is included at:

`examples/dashboard-built-in.yaml`

### 🫧 Bubble Card

An optional Bubble Card example is included at:

`examples/dashboard-bubble-card.yaml`

Bubble Card is not required by Prayer Hub itself.

## 🎨 Themes

Prayer Hub includes five landscape display themes:

- 🌅 **Fajr** — dawn blue
- ☀️ **Dhuhr** — daylight blue
- 🌤️ **Asr** — warm afternoon
- 🌇 **Maghrib** — sunset rose/amber
- 🌙 **Isha** — moonlit navy

The video switches to full-screen landscape playback after the countdown.

## 📖 Qur'an reminders and du'a

Prayer Hub does not call an external content API.

The curated local content is stored at:

`custom_components/prayer_hub/static/content.json`

Each item contains:

```json
{
  "reference": "Qur’an 20:14",
  "arabic": "...",
  "english": "..."
}
```

The display selects content deterministically using the date and prayer name.

If you edit `content.json`, keep it valid JSON and preserve the `reference`, `arabic` and `english` keys.

## 🔐 Privacy and security

Prayer Hub stores configuration locally in Home Assistant.

The playback-finished callback uses a random token generated on your own Home Assistant installation. Do not post that token publicly.

Before filing GitHub issues, remove:

- Home Assistant access tokens
- callback tokens
- private domain names
- exact local IP addresses unless necessary
- Fully Kiosk passwords
- private device IDs

## ▶️ YouTube notes

The default videos are configurable.

YouTube owners can change embedding permissions or remove videos at any time. Browser/WebView autoplay policies may also prevent unmuted autoplay. Prayer Hub includes a tap-to-play fallback.

Users are responsible for selecting media they are permitted to play and for complying with YouTube's terms.

## 🔄 Updating and compatibility

Prayer Hub does **not** have a regular update schedule.

If a newer release is published, HACS custom-repository users can update from HACS. Manual users can download the newer release and replace:

`custom_components/prayer_hub`

then restart Home Assistant.

Your Home Assistant config entry should normally remain in place between compatible versions.

### ⚠️ Compatibility notice

This release was tested as a working snapshot of Prayer Hub at the time it was published.

Because Prayer Hub depends on several separate projects and services, future changes to any of the following may require community fixes:

- Home Assistant
- HACS
- London Unified Prayer Times (LUPT)
- Fully Kiosk Browser / its Home Assistant integration
- Android WebView or browser autoplay behaviour
- YouTube embedding/playback

If the project is no longer updated, users can continue using a compatible release, fork the repository, or maintain their own version.


## 🍴 Publishing your own fork

If you fork or clone this repository:

1. Replace every occurrence of:

   `YOUR_GITHUB_USERNAME`

   with your GitHub username.

2. Update `custom_components/prayer_hub/manifest.json`.
3. Add a GitHub repository description.
4. Add repository topics such as:

   `home-assistant`, `hacs`, `prayer-times`, `fully-kiosk`, `islamic`, `home-automation`

5. Enable GitHub Issues.
6. Push the repository.
7. Check the **HACS validation** and **Hassfest** workflows.
8. Create a GitHub **Release** (not only a tag), for example:

   `v2.3.2`

## 🐙 Creating the GitHub repository

If you are publishing this package for the first time:

1. On GitHub, click **New repository**.
2. Name it:

   `prayer-hub`

3. Set it to **Public** if you want other people to install it through HACS.
4. Do not initialise it with another README or licence; this package already includes them.
5. Create the repository.
6. Extract this release package locally.
7. Upload the **contents** of the repository package so the root of GitHub contains:

```text
.github/
brand/
custom_components/
examples/
.gitignore
CHANGELOG.md
CONTRIBUTING.md
hacs.json
LICENSE
README.md
SECURITY.md
```

Do not upload everything inside an extra `prayer-hub/` directory.

8. Edit the two placeholder URLs in `manifest.json`.
9. Commit the changes.
10. Wait for GitHub Actions to finish.
11. Open **Releases → Draft a new release**.
12. Tag the release `v2.3.2`.
13. Publish it.

Other users can then install the repository through HACS as a custom integration.

## 🧩 HACS distribution

Prayer Hub is designed to be installed through **HACS as a custom repository**.

It is not currently intended to be submitted to the default searchable HACS catalogue. This keeps distribution simple without implying an ongoing maintenance or release commitment.

Users who prefer not to use HACS can install the exact same integration manually using the instructions above.


## 🤝 Support and contributions

There is no guaranteed support response time for this project.

If something stops working after an upstream update, check existing GitHub issues first. Community troubleshooting, forks and pull requests are welcome, but fixes may not be reviewed or released promptly.

When reporting a problem, never publish Home Assistant tokens, callback tokens, passwords or other credentials.

## 📜 Licence

MIT. See [LICENSE](LICENSE).

## 🙏 Credits

Prayer Hub relies on the wider Home Assistant ecosystem, including:

- Home Assistant
- HACS
- London Unified Prayer Times (`homeassistant-lupt`)
- Fully Kiosk Browser

Prayer Hub is not affiliated with East London Mosque, Home Assistant, HACS, Fully Kiosk, or YouTube.
