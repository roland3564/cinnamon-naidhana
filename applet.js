const Applet = imports.ui.applet;
const GLib = imports.gi.GLib;
const Mainloop = imports.mainloop;

class NaidhanaApplet extends Applet.TextApplet {
    constructor(metadata, orientation, panelHeight, instanceId) {
        super(orientation, panelHeight, instanceId);
        this.set_applet_tooltip("Naidhana Detector: shows Naidhana planetary positions");

        this._scriptPath = GLib.build_filenamev([
            GLib.get_home_dir(),
            ".local",
            "share",
            "cinnamon",
            "applets",
            "naidhana-detector@n1",
            "naidhana-detector.py"
        ]);

        this._update();
    }

    _update() {
        try {
            let [ok, stdout, stderr, status] = GLib.spawn_command_line_sync(`python3 "${this._scriptPath}"`);
            if (ok && status === 0) {
                let output = stdout.toString().trim();
                this.set_applet_label(output || "—");
            } else {
                this.set_applet_label("Err");
            }
        } catch (e) {
            this.set_applet_label("Err");
        }

        Mainloop.timeout_add_seconds(300, () => {
            this._update();
            return false;
        });
    }
}

function main(metadata, orientation, panelHeight, instanceId) {
    return new NaidhanaApplet(metadata, orientation, panelHeight, instanceId);
}

