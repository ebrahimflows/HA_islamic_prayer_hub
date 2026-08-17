# Publishing Prayer Hub on GitHub

Prayer Hub is intended to be a **stable, as-is community release**, not an actively maintained HACS catalogue project.

## One-time publication

- [ ] Create a public GitHub repository named `prayer-hub`.
- [ ] Upload the repository contents at the repository root.
- [ ] Replace `YOUR_GITHUB_USERNAME` in `custom_components/prayer_hub/manifest.json`.
- [ ] Add a short repository description.
- [ ] Add topics such as `home-assistant`, `hacs`, `prayer-times`, `fully-kiosk`, `islamic`, `home-automation`.
- [ ] Confirm HACS validation passes.
- [ ] Confirm Hassfest passes.
- [ ] Publish the known-working release as `v2.3.2`.
- [ ] Test installation once through HACS as a custom repository.
- [ ] Test the manual ZIP installation instructions.

## Distribution

Recommended:

**HACS custom repository**

Users add the public repository URL to HACS as an Integration.

Also supported:

**Manual installation**

Users download the release and copy `custom_components/prayer_hub` into their Home Assistant configuration.

## Maintenance expectations

There is no planned release cadence.

Do not submit Prayer Hub to the default HACS catalogue unless you later decide that you want to actively maintain the project.

Future fixes or releases are optional. Community forks and pull requests can keep the project useful if the original repository becomes inactive.

## If you do publish another release

- [ ] Update the version in `custom_components/prayer_hub/manifest.json`.
- [ ] Update `CHANGELOG.md`.
- [ ] Test a manual prayer run.
- [ ] Test Fajr separately.
- [ ] Confirm TV mute restoration.
- [ ] Confirm lights that were off stay off.
- [ ] Confirm the tablet returns to the configured dashboard.
- [ ] Confirm HACS validation and Hassfest pass.
