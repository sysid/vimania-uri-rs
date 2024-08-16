#!/usr/bin/env bash
set +ex
#vim '+Vader!*' && echo Success || echo Failure' && echo Success || echo Failure

source ~/dev/binx/profile/sane_fn.sh

prep-db() {
  echo "-M- Creating vader DB: $(pwd)"
  twpushd "$PROJ_DIR/pythonx/vimania_uri_/db"
  [[ -f todos.db  ]] && rm -v todos.db
  alembic upgrade head
  readlink -f todos.db
  cp -v todos.db "$PROJ_DIR/tests/data/vader.db"
  twpopd
}

prep-twbm() {
  echo "-M- Looking for test google entry in twbm to delete if necessary."
  id=$(TWBM_DB_URL=sqlite://///Users/Q187392/vimwiki/buku/bm.db twbm search -t vimania --np '"www.google.com"')
  if [ ! -z "$id" ]; then
    Cyan "-M- Deleting test google entry in twbm"
    TWBM_DB_URL=sqlite://///Users/Q187392/vimwiki/buku/bm.db twbm delete "$id"
  else
    Green "-M- google test entry not found. All good."
  fi
}

#cp -v data/todos.db.empty data/vader.db

if [ -z "$1" ]; then
    echo "-E- no testfiles given."
    echo "runall: $0 '*'"
    exit 1
fi

################################################################################
# main
################################################################################
#prep-db  # no DB required
prep-twbm

vim -Nu <(cat << EOF
filetype off
set rtp+=~/.vim/plugged/vader.vim
set rtp+=~/.vim/plugged/vim-misc
set rtp+=~/.vim/plugged/scriptease
set rtp+=~/dev/vim/tw-vim
set rtp+=~/dev/vim/vimania-uri
filetype plugin indent on
syntax enable

" TWBM INTEGRATION:
let g:vimania_uri__twbm_integration=1
" URI extensions
let g:vimania_uri__extensions=['.md', '.txt', '.py']

let g:twvim_debug = 1
let g:os = 'Darwin'
if g:twvim_debug | echom "-D- Debugging is activated." | endif

" required by tw-vim
let g:twvim_config = {
      \ 'diary_path': '/Users/Q187392/vimwiki/diary',
\ }


" to avoid prompting
set shortmess+=at
"set cmdheight=200
packadd cfilter

EOF) "+Vader! $1" && Green Success || Red Failure
