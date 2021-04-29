# -*- coding: utf-8 -*-

def resume_scan(url, thread, wordlist, recur, redirect, js, backup):
    recur_ = "\033[32mTrue\033[0m" if recur else "\033[31mFalse\033[0m"
    js_ = "\033[32mTrue\033[0m" if js else "\033[31mFalse\033[0m"
    backup_ = ' '.join(["\033[32m{}\033[0m".format(b) for b in backup]) if backup else "\033[31mFalse\033[0m"
    redirect_ = "\033[32mTrue\033[0m" if redirect else "\033[31mFalse\033[0m"
    print("""
 \033[36m Target:                 \033[0m \033[32m{}\033[0m
 \033[36m Threads:                \033[0m \033[32m{}\033[0m
 \033[36m Wordlist:               \033[0m \033[32m{}\033[0m
 \033[36m Recursive:              \033[0m {}
 \033[36m Follow Redirects:       \033[0m {}
 \033[36m Javascript Check:       \033[0m {}
 \033[36m Backup extension: 	  \033[0m {}
___________________________________________________________________
    """.format(url, thread, wordlist, recur_, redirect_, js_, backup_))