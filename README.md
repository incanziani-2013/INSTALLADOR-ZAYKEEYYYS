# ZAY KEYS Installer — v1.0.1

Windows 10/11 x64 installer project for the supplied ZAY KEYS VST3 bundle.

## What it installs

- `payload/ZAY KEYS.vst3` into the selected VST3 folder (default: `C:\Program Files\Common Files\VST3\ZAY KEYS.vst3`).
- Optional documentation into `Documents\GOLDMINE AUDIO\ZAY KEYS\Documentation`.
- A Windows uninstaller registered by Inno Setup.

The installer preserves the VST3 bundle's internal folder structure. It does not modify the plugin binary or its internal UI.

## Build the EXE

The `.exe` must be compiled on Windows with Inno Setup 6:

1. Install Inno Setup 6.
2. Open `installer/ZayKeysInstaller.iss` in Inno Setup Compiler.
3. Press **Compile**.
4. The output will be created in `output/`.

Alternatively, create a GitHub repository from the contents of this folder (so `.github` is at the repository root), then run **Actions → Build ZAY KEYS Installer → Run workflow**. The workflow validates the payload, compiles the installer and uploads the EXE plus a source ZIP as an artifact.

## Install

1. Run `ZAY_KEYS_Installer_v1.0.1_Windows.exe`.
2. Approve the Windows administrator prompt (required for the default system VST3 folder).
3. Keep the VST3 component selected. Documentation is optional.
4. Finish installation.
5. In FL Studio, open **Options → Manage plugins → Find installed plugins** and scan for ZAY KEYS.

## Uninstall

Use **Settings → Apps → Installed apps → ZAY KEYS VST3 → Uninstall**, or the Start Menu uninstaller. Inno Setup removes the files installed by this package; it does not remove unrelated VST3 plugins.

## Design assets

The `assets/generated/` folder contains the supplied ZAY KEYS blue/cyan Frutiger Aero artwork, keyboard artwork, icon, and original asset-generation source. The Inno Setup wizard uses the ZAY KEYS icon and a branded side illustration. The stock Inno Setup progress UI is retained for reliable Windows installation and rollback behavior.

## Important notes

- This project packages the supplied compiled VST3 binary; it does not rebuild the plugin source.
- The original uploaded archive had malformed directory entries and did not include a complete installer script or workflow. This project has a normalized folder layout and adds those missing build files.
- The EXE is not yet compiled or runtime-tested in this Linux environment. Use the GitHub Actions Windows build or compile with Inno Setup on Windows before distributing it.
- The plugin README notes that JUCE licensing and the distribution rights for the bundled SoundFont should be confirmed before commercial redistribution.
