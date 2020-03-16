_isos_post() {
    local cur
    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    prev="${COMP_WORDS[COMP_CWORD - 1]}"
    opts="--host --distri --version --flavor --arch --iso --noiso --build --test --alias --debug --params --nostartafter --branch --priority --github-user --force"
    if [[ ${cur} == -* || ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
        return 0
    fi
    case "${prev}" in
    --version)
        COMPREPLY=($(compgen -W "15-SP2 12-SP5" -- ${cur}))
        ;;
    --host)
        COMPREPLY=($(compgen -W "https://openqa.suse.de http://autobot" -- ${cur}))
        ;;
    --distri)
        COMPREPLY=($(compgen -W "sle opensuse" -- ${cur}))
        ;;
    --flavor)
        COMPREPLY=($(compgen -W "Online Azure-BYOS  EC2-HVM-ARM" -- ${cur}))
        ;;
    esac
}

complete -F _isos_post isos_post
