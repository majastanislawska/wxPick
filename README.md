# wxPick

wxPick is a desktop GUI for [Pick](https://github.com/majastanislawska/pick) (&#x1D745;&#x1D450;&#x1D458;)
which in turn is a spinoff of [Klipper](https://www.klipper3d.org/) that focuses on Pick and Place machines.
it helps with working with [OpenPNP](https://openpnp.org/) removing dependency on Moonraker, Mainsail/Fluidd and RaspberryPi while providing useful features.

Main feature is a tcp server on localhost:8888 that you can configure your OpenPNP to connect to, that relays gcode commands to Pick's unix socket.\
You can have multiple clients connected and each will only see responses to own commands.\
That might be used to have extra network enabled gcode pendant like those several esp32 based that exists on internet.(ofc you need to hack code to let it bind on all interfaces, not just localhost, for that to work).\
This feature will not work with stock Klipper unless you patch it with this at least this [patch](https://github.com/majastanislawska/pick/commit/9334d85f6548f0f3ee03224bbce302d95b25aa4f) and some other too.

Besides that, there's:

* a "gcode console" where you can type commands, and view all Pick (klipper) replies (uses standard klipper's "gcode/subscribe_output")
* a log console that shows all Pick (klipper) APIServer "webhooks" traffic on it's Unix Socket.
* Camera support based on openpnp-capture, so if your cmera works witl openpnp it will work here, camera params (exposure, focus, brigthess etc) are supported.
* Camera overlays: Two kinds:

  * one is merged with camera frame (`cv2.addWeighted(frame, 0.65, self.frameoverlay, 0.35, 0)`) before zooming.
  This is intended for heatmaps ant other outputs of image processing.
  you can grab own camera frame, process it and than assign it to `camera.frameoverlay` to be displayed.
  * second is in form of callback that is called right before widget is rendered to xwBitmap. create `callback(w,h,canvas_rgb)` and append it to `camera.canvas_overlays` list. `w` and `h` is size of paintarea of camera widget, i may add coordinates of rectangle where camera frame actually is in it with scaling factor etc in the future.

* Camera window, with controls for light and zoom (have `TOP_LIGHT S={0|1}` in Klipper config to control your camera light)
* a Jog Panel
* a Toolbar with buttons for most important commands (emergency shutdown and restart), it also serves as a boilerplate on how to create own toolbars with other commands.
* Object Browser. A treeview panel that let you see whole internal state of Pick (Klipper)
* jog buttons for rotary axes do 45 and 90 move instead of 50 and 100. Quite practical when your rotary axes are in degrees
* graphs.
* easily expandable modular design and code

This is very early stage project, a lot of things may change.

## installation

Grab &#x1D745;&#x1D450;&#x1D458; [from here](https://github.com/majastanislawska/pick) and install and configure it like any other Klipper, you need to start it with unix socket enabled though: add `-a /tmp/pick_socket` to commandline.

you can create own venv for wxPick, or you can ask VSCode to do it for you, or you can use python from Pick environment - just add wxPick's requirements `pip install -r requirements.txt`

dont forget to cline this repo wth `--recurse-submodules` to get sources for camera library.
`make capture` should build openpnp-capture and place it in `lib/` dir.

On Mac you can use `make app` to create standalone application that can be dropped into /Applications folder.
