These are user contributed plugins for [pwnagotchi](https://github.com/evilsocket/pwnagotchi), some of them have not been 
completely tested by the dev team, **use them at your own risk**.

In order to use these plugins, clone the repository anywhere on your unit and then add its path to `/etc/pwnagotchi/config.toml` as:

```toml
main.custom_plugins = "/path/to/this/folder"
```

Each plugin has its own configuration than must be part of the `main.plugins` section. If for instance you want to enable
the auto_backup plugin, you need to edit your config.toml and add this:

```toml
main.custom_plugins = "path/to/this/folder"
main.plugins.auto_backup.enabled = true
main.plugins.auto_backup.interval = 1 # every day
main.plugins.auto_backup.max_tries = 0 # 0=infinity
main.plugins.auto_backup.files = [
  "/root/brain.nn",
  "root/brain.json",
  "/root/.api-report.json",
  "/root/handshakes/",
  "/root/peers/",
  "/etc/pwnagotchi/",
  "var/log/pwnagotchi.log"
]
main.plugins.auto_backup.commands = [
  "tar czf /root/pwnagotchi-backup.tar.gz {files}"
]
```

## License

The user contributed plugins are released under the GPL3 license.
