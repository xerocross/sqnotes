#!/bin/bash

_sqnotes_completion() {
    local cur prev commands options subcommands subsubcommands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    commands="sqnotes"
    options=""
    subcommands="new edit man"
    mansubcommands="main encryption"

    case "$prev" in
        "")
            COMPREPLY=( $(compgen -W "$commands" -- "$cur") )
            ;;
        sqnotes)
            COMPREPLY=( $(compgen -W "$subcommands" -- "$cur") )
            ;;
        man)
            COMPREPLY=( $(compgen -W "$mansubcommands" -- "$cur") )
            ;;
        *)
            ;;
    esac

    return 0
}

complete -F _sqnotes_completion sqnotes