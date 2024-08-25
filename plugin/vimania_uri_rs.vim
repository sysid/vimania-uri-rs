" vim: set foldmethod=marker fdl=0 ts=2 sts=2 sw=2 tw=80 :
"
" Reload and Compatibility Guard {{{ "
" ============================================================================
if exists('g:loaded_vimania_uri_rs') && g:loaded_vimania_uri_rs == 1
    finish
endif
let s:save_cpo = &cpo
set cpo&vim
" }}} Reload Guard "

" Python Guard {{{ "
if !has("python3")
  echohl ErrorMsg | echo  "ERROR: vim has to be compiled with +python3 to run this" | echohl None
  finish
endif
" }}} Python Guard "

" Globals {{{ "
" ============================================================================
if !exists("g:twvim_debug")
  let g:twvim_debug = 0
endif
if g:twvim_debug | echom "-D- Sourcing " expand('<sfile>:p') | endif

let start_time = reltime()
let s:script_dir = fnamemodify(resolve(expand('<sfile>', ':p')), ':h')

" full path to the current script file, without its file extension
let g:vimania#PythonScript = expand('<sfile>:r') . '.py'
TwDebug "Vimania-Uri PythonScript: " . g:vimania#PythonScript

let g:vimania_uri_extensions = get(g:, "vimania_uri_extensions", ['.md','.txt','.rst','.py','.conf','.sh','.json','.yaml','.yml'])
TwDebug "Vimania-Uri Extensions: " . join(g:vimania_uri_extensions, ", ")

let g:vimania_uri_twbm_integration = get(g:, "vimania_uri_twbm_integration", 0)
TwDebug "Vimania-Uri twbm integration: " . g:vimania_uri_twbm_integration

let g:vimania_uri_rs_default_vim_split_policy = get(g:, "vimania_uri_rs_default_vim_split_policy", "none")
let s:is_vimania_uri_rs_engine_loaded = 0
TwDebug "elapsed time:" . reltimestr(reltime(start_time))
" }}} Globals "

" Vimania-Uri Engine {{{ "
" ============================================================================
execute 'py3file ' . g:vimania#PythonScript
"py3file /Users/Q187392/dev/vim/vimania/plugin/python_wrapper.py
let s:is_vimania_uri_rs_engine_loaded = 1
TwDebug "elapsed time:" . reltimestr(reltime(start_time))
" }}} Vimania-Uri Engine "

" Functions {{{ "
" ============================================================================
function! s:HandleMd(save_twbm)
  python3 xUriMgr.call_handle_md2(vim.eval('a:save_twbm'))
  redraw!
endfunction
command! HandleMd :call <sid>HandleMd(0)
command! HandleMdSave :call <sid>HandleMd(1)

function! GetURLTitle(url)
  call TwDebug(printf("Vimania args: %s", a:url))
  python3 xUriMgr.get_url_title(vim.eval('a:url'))
  "call TwDebug(printf("title: %s", g:vimania_url_title))
endfunction
command! -nargs=1 GetURLTitle call GetURLTitle(<f-args>)

function! VimaniaEdit(args)
  call TwDebug(printf("Vimania args: %s", a:args))
  python3 xUriMgr.edit_vimania(vim.eval('a:args'))
endfunction
command! -nargs=1 VimaniaEdit call VimaniaEdit(<f-args>)
"nnoremap Q :VimaniaEdit /Users/Q187392/dev/vim/vimania/tests/data/test.md# Working Examples<CR>

function! VimaniaDebug()
  "call TwDebug(printf("Vimania args: %s, path: %s", a:args, a:path))
  python3 xUriMgr.debug()
endfunction
command! -nargs=0 VimaniaDebug call VimaniaDebug()
"noremap Q :VimaniaDebug<CR>

function! VimaniaThrowError()
  "call TwDebug(printf("Vimania args: %s, path: %s", a:args, a:path))
  python3 xUriMgr.throw_error()
endfunction
command! -nargs=0 VimaniaThrowError call VimaniaThrowError()
"noremap Q :VimaniaDebug<CR>

function! VimaniaDeleteTwbm(args)
  call TwDebug(printf("Vimania args: %s", a:args))
  " Prompt the user for confirmation
  let l:confirmation = input("Delete also from bkmr database? (y/n): ")
  if l:confirmation ==? 'y'
    python3 xUriMgr.delete_twbm(vim.eval('a:args'))
    echo "Bookmark deleted."
  else
    echo "Deletion canceled."
  endif
endfunction
command! -nargs=1 VimaniaDeleteTwbm call VimaniaDeleteTwbm(<f-args>)
"noremap Q :VimaniaDeleteTodo - [ ] todo vimania<CR>

function s:PasteMDLink()
  let url = getreg("+")
  echo(url)
  call GetURLTitle(url)
  let mdLink = printf("[%s](%s)", g:vimania_url_title, url)
  execute "normal! a" . mdLink . "\<Esc>"
endfunction
noremap <SID>PasteMDLink :call <SID>PasteMDLink()<CR>

let s:link_pattern = '\(\[.\{-}\](.\{-})\|\[.\{-}\]\[.\{-}\]\)'
function! s:_vimania_uri_rs_find_next_link()
    call search(s:link_pattern, 'w')
endfunction
command! VimaniaUriFindLinkNext :call s:_vimania_uri_rs_find_next_link()

function! s:_vimania_uri_rs_find_prev_link()
    call search(s:link_pattern, 'bw')
endfunction
command! VimaniaUriFindLinkPrev :call s:_vimania_uri_rs_find_prev_link()
" }}} Functions "

" Mappings {{{ "
" ============================================================================
nnoremap  <unique> <script> <Plug>(HandleMd) <Cmd>HandleMd<CR>
if !hasmapto('<Plug>HandleMd', 'n')
    nmap go <Plug>(HandleMd)
endif

nnoremap <unique> <script> <Plug>(HandleMdSave) <Cmd>HandleMdSave<CR>
if !hasmapto('<Plug>HandleMdSave', 'n')
    nmap goo <Plug>(HandleMdSave)
endif

noremap <unique> <script> <Plug>(UriPasteMDLink) <SID>PasteMDLink
if !hasmapto('<Plug>UriPasteMDLink', 'n')
    nmap <unique> <Leader>vl <Plug>(UriPasteMDLink)
endif

nnoremap <Plug>(VimaniaUriFindLinkNext) :VimaniaUriFindLinkNext<CR>
nnoremap <Plug>(VimaniaUriFindLinkPrev) :VimaniaUriFindLinkPrev<CR>
" }}} Mappings "

" augroup {{{ "
" ============================================================================
augroup Vimania-Uri
 autocmd!
" removes URL (pattern) from twbm
 autocmd TextYankPost *.md
    \ if len(v:event['regcontents']) == 1 && v:event['regcontents'][0] =~? 'http[s]\=://' && v:event['operator'] == 'd' && ! v:event['visual']
    \ | call VimaniaDeleteTwbm(v:event['regcontents'][0])
    \ | endif
augroup END
" }}} augroup "

" helper commands {{{ "
if exists('g:twvim_init')
  finish
endif
let g:twvim_init = 1

command -bang -range=0      -nargs=? -complete=expression TwDebug
    \ if g:twvim_debug == 1 |
    \   if !empty(<q-args>) |
    \     let file = expand('%:p:t') |
    \     echom printf("-D- %s: %s", file, eval(scriptease#prepare_eval(<q-args>))) |
    \   endif |
    \ endif

command -bang -range=0      -nargs=? -complete=expression TwLog
    \   if !empty(<q-args>) |
    \     let file = expand('%:p:t') |
    \     echom printf("-M- %s: %s", file, eval(scriptease#prepare_eval(<q-args>))) |
    \   endif |

command -bang -range=0      -nargs=? -complete=expression TwErr
    \   if !empty(<q-args>) |
    \     let file = expand('%:p:t') |
    \     echohl ErrorMsg
    \     echom printf("-E- %s: %s", file, eval(scriptease#prepare_eval(<q-args>))) |
    \     echohl None
    \   endif |
" }}} helper commands "

" Reload and Compatibility Guard {{{ "
" ============================================================================
let g:loaded_vimania_uri_rs = 1
let &cpo = s:save_cpo
TwDebug "elapsed time:" . reltimestr(reltime(start_time))
" }}} Reload and Compatibility Guard "