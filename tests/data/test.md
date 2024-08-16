# Heading
some example text

# Table of Contents

- [Heading](#heading)
- [Table of Contents](#table-of-contents)
    - [Second Heading](#second-heading)
- [Working Examples](#working-examples)
    - [Config](#config)
    - [Code](#code)

## Second Heading

Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.

, mapping exists## Heading2
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.
```bash
echo 2
echo 1
```

hello [there](#second-heading)
<kbd>ctrl</kbd>
**bold**, *italic*

"bla","blub"
"x","y"

```bash
URIPositioningPatternAdd! \[[^]]*\](\zs[^)]\+) markdown
[Link description](http://www.slashdot.org/)
[pdf: vimtool](pdf:vimtool/vimania.pdf)

file://~/vimtool/vimtool/vimania.pdf
[file: vimtool](file://~/vimtool/vimtool/vimania.pdf)
![vimtool.png](vimtool.png)
```
[bla](bla)

# Working Examples
from codebase:
file:///\%(\K[\/.]*\)\+': ':call TextobjUriOpen()',
file:///\%(\k[\/.]*\)\+': ':call TextobjUriOpen()',  mit digits, no dashes!!!

## Config
```vim
URIPatternAdd! xxx://\%(\k[\/.]*\)\+ :echo\ "%s"
URIPatternAdd! xxx://\%(\([^()]\+\)\) :echom\ "%s"

URIPatternAdd! xxx://\%(\([^()]\+\)\) :silent\ !open\ "%s"
```

xxx://xxx/xxx.pdf
xxx://$HOME/dev/vim/vim-textobj-uri/test/xxx//xxx.pdf
[xxx](xxx://$HOME/dev/vim/vim-textobj-uri/test/xxx//xxx.pdf)

yyy://$HOME/dev/vim/vim-textobj-uri/test/xxx//xxx.pdf

zzz::https://google.com
zzz::"https://google.com"
zzz::'https://google.com'
zzz::https://google.com#bla

zzz::https:// $HOME/dev/vim/vim-textobj-uri/test/xxx//xxx.pdf
zzz::https://$HOME/dev/vim/vim-textobj-uri/test/xxx//xxx.pdf
zzz::.....://$HOME/dev/vim/vim-textobj-uri/test/xxx//xxx.pdf
[zzz attempt](zzz::https://$HOME/dev/vim/vim-textobj-uri/test/xxx//xxx.pdf)

### gx
[xxx](xxx/xxx.pdf)


## Code
file2:///Users/Q187392/dev/vim/vim-textobj-uri/test/xxx//xxx.pdf
[file: xxx](file:///Users/Q187392/dev/vim/vim-textobj-uri/test/xxx//xxx.pdf)

[D: DE-39 department](file2:///Volumes/DE-Org/DE-3/DE-39)
some text http://www.slashdot.org/ some more text
