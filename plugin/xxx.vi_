" reverse_line.vim
if has('python3')
    python3 << EOF
import vim
from vimania_uri_rs import reverse_line

def reverse_current_line():
    line = vim.current.line
    reversed_line = reverse_line(line)
    vim.current.line = reversed_line
EOF

    command! ReverseLine :py3 reverse_current_line()
endif
