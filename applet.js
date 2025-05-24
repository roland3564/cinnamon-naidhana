const Applet = imports.ui.applet;
const GLib = imports.gi.GLib;
const Mainloop = imports.mainloop;
const Lang = imports.lang;

class NaidhanaApplet extends Applet.TextApplet {
    constructor(metadata, orientation, panelHeight, instanceId) {
        super(orientation, panelHeight, instanceId);
        this.set_applet_tooltip("Naidhana Detector: shows Naidhana planetary positions");

        this._scriptPath = GLib.build_filenamev([
            GLib.get_home_dir(),
            ".local", "share", "cinnamon", "applets",
            "naidhana-detector@n1", "naidhana-detector.py"
        ]);

        this._outputPath = GLib.build_filenamev([
            GLib.get_home_dir(),
            ".local", "share", "cinnamon", "applets",
            "naidhana-detector@n1", "output.txt"
        ]);

        this._update();  // Initial run
    }

    _runScriptAsync() {
        GLib.spawn_command_line_async(`python3 "${this._scriptPath}"`);
    }

    _readOutput() {
        try {
            let [ok, contents] = GLib.file_get_contents(this._outputPath);
            if (ok) {
                this.set_applet_label(contents.toString().trim() || "—");
            } else {
                this.set_applet_label("Err");
            }
        } catch (e) {
            this.set_applet_label("Err");
        }
    }

    _update() {
        this._runScriptAsync();  // Non-blocking
        Mainloop.timeout_add_seconds(2, () => {  // Delay to allow script to finish
            this._readOutput();
            return false;
        });

        Mainloop.timeout_add_seconds(300, () => {  // Schedule next update
            this._update();
            return false;
        });
    }
}

function main(metadata, orientation, panelHeight, instanceId) {
    return new NaidhanaApplet(metadata, orientation, panelHeight, instanceId);
}

