#!/usr/bin/env bash
set +ex
#vim '+Vader!*' && echo Success || echo Failure' && echo Success || echo Failure

_RESET="\e[0m"
_RED="\e[91m"
_GREEN="\e[92m"
_YELLOW="\e[93m"
_CYAN="\e[96m"

Red () {
    printf "${_RED}%s${_RESET}\n" "$@"
}
Green () {
    printf "${_GREEN}%s${_RESET}\n" "$@"
}
Cyan () {
    printf "${_CYAN}%s${_RESET}\n" "$@"
}

if [ -z "$1" ]; then
    echo "-E- no testfiles given."
    echo "runall: $0 '*'"
    exit 1
fi

################################################################################
# main
################################################################################
vim -Nu <(cat << EOF
filetype off
set rtp+=~/.vim/plugged/vader.vim
set rtp+=~/.vim/plugged/vim-misc
set rtp+=~/.vim/plugged/scriptease
set rtp+=~/dev/vim/tw-vim
set rtp+=~/dev/vim/vimania-uri-rs
filetype plugin indent on
syntax enable

" TWBM INTEGRATION:
let g:vimania_uri_twbm_integration=1
" URI extensions
let g:vimania_uri_extensions=['.md', '.txt', '.py']
let g:vimania_uri_twbm_integration=1

let g:twvim_debug = 1
let g:os = 'Darwin'
if g:twvim_debug | echom "-D- Debugging is activated." | endif

" to avoid prompting
set shortmess+=at
"set cmdheight=200
packadd cfilter

EOF) "+Vader! $1" && Green Success || Red Failure
