" vim: fdm=marker ts=2 sts=2 sw=2 fdl=0
" convert_string.vim
if g:twvim_debug | echom "-D- Sourcing " expand('<sfile>:p') | endif
let s:script_dir = fnamemodify(resolve(expand('<sfile>', ':p')), ':h')

" save current time
let start_time = reltime()

if !has("python3")
  echohl ErrorMsg | echo  "ERROR: vim has to be compiled with +python3 to run this" | echohl None
  finish
endif

" only load it once
if exists('g:vimania_uri_wrapper')
  finish
endif

" echo elapsed time expressed in seconds
TwDebug "elapsed time:" . reltimestr(reltime(start_time))

let g:vimania#PythonScript = expand('<sfile>:r') . '.py'
TwDebug "Vimania PythonScript: " . g:vimania#PythonScript

execute 'py3file ' . g:vimania#PythonScript
"py3file /Users/Q187392/dev/vim/vimania/pythonx/vimania/entrypoint/python_wrapper.py
"py3file /Users/Q187392/dev/vim/vimania/plugin/python_wrapper.py

TwDebug "elapsed time:" . reltimestr(reltime(start_time))

function! GetURLTitle(url)
  call TwDebug(printf("Vimania args: %s", a:url))
  python3 xUriMgr.get_url_title(vim.eval('a:url'))
  "call TwDebug(printf("title: %s", g:vimania_url_title))
endfunction
command! -nargs=1 GetURLTitle call GetURLTitle(<f-args>)

" DEPRECATED
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
  python3 xUriMgr.delete_twbm(vim.eval('a:args'))
endfunction
command! -nargs=1 VimaniaDeleteTwbm call VimaniaDeleteTwbm(<f-args>)
"noremap Q :VimaniaDeleteTodo - [ ] todo vimania<CR>

TwDebug "elapsed time:" . reltimestr(reltime(start_time))
let g:vimania_uri_wrapper = 1
