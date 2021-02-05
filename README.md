These are user contributed plugins for [pwnagotchi](https://github.com/evilsocket/pwnagotchi), some of them have not been 
completely tested by the dev team, **use them at your own risk**.

In order to use these plugins, clone the repository anywhere on your unit and then add its path to `/etc/pwnagotchi/config.toml` as:

```yaml
main.custom_plugins = "/path/to/this/folder"
```
This line (main.custom_plugins = "") should already be in your config.toml. You just need to update the path.


Each plugin has its own configuration which is created in config.toml when you activate the plugin. 
```

## License

The user contributed plugins are released under the GPL3 license.
