# Demo

## Demo Navigation
Type `go` to navigate links.

This [link](https://sysid.github.io/rewriting-a-vim-plugin-in-rust-vimania-uri-rs/) will be opened inside the browser.

This [link](./foo.md) will open `./foo.md` inside vim.
This [link](./foo.md:3) will open `./foo.md` and jump to line 3.
This [link](./foo.md#Anchor) will open `./foo.md` and jump to heading2

This [Project Home]($HOME/dev/s/public/vimania-uri-rs) directory will be opened inside file browser, variables expanded

This [Powerpoint: vimania-uri-rs]($HOME/dev/s/public/vimania-uri-rs/doc/vimania-uri.pptx)  will open in Powerpoint

Document internal linking works, too:
[link](#Anchor) to the heading Anchor:

Reference style [links][ref-style-link] will open http://example.com in browser

## Demo Pasting Links
Type `vl` to paste a markdown link.


## Other Demo Resources
### Anchor
Will jump here.

[ref-style-link]: http://example.com

<a name="AnchorExample">This is an anchor</a>
<a id="AnotherAnchor">Another anchor here</a>
