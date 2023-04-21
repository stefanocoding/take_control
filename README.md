Control your Apogee Duet (USB) on Linux! 
===

This Python script and Apogee Duet (USB) speak the same language :smile:

The interface works great out of the box using ALSA for recording and playing. However, I didn't find a way to control the settings like I was able to do on macOS.

I will read about ALSA and ways to integrate directly with `alsamixer` or something like that, but for the time being, the script works and solves the problem.

Installation (Ubuntu)
---
```sh
$ sudo apt install python3-usb python3-wxgtk4.0
```

How to use
---
It's organized in a similar way than the application for macOS.
_You have to reopen the application to see the last changes, if the change affected more than one control._ It's not a big deal for me because I usually change the settings once (like change the input type to Instrument or something like that), but I understand that it may bother some users.

```sh
$ sudo ./take_control.py
```

Things to improve
---
1. Update all the controls related to a setting that changed.
1. Update controls when some setting is changed physically (using the knob or touchpads).
1. Find a way to not require using `sudo` but without compromising the entire system (like adding the user to a group that disables the requirement of `sudo` for sensitive actions).
1. Add support for changing the assigned functions of the touchpads.
