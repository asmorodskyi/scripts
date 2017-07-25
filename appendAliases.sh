#!/bin/sh
modify_file=~/.bashrc
alias_array[1]="alias gco=\"git checkout\""
alias_array[2]="alias gpl=\"git pull\""
alias_array[3]="alias gph=\"git push\""
alias_array[4]="alias gst=\"git status\""
alias_array[5]="alias gad=\"git add .\""
alias_array[6]="alias gcim=\"git commit --amend\""
alias_array[7]="alias gphf=\"git push -f\""
alias_array[8]="alias grhh=\"git reset --hard HEAD\""
alias_array[9]="alias gba=\"git branch -a\""
alias_array[10]="alias gci=\"git commit\""
alias_array[11]="alias gdf=\"git diff\""
alias_array[12]="alias hgrep=\"history | grep\""
alias_array[13]="alias gcon=\"/scripts/git/git_checkout_new.sh\""
alias_array[14]="alias gbd=\"git branch -D\""
alias_array[15]="alias grm=\"/scripts/git/rebase.sh\""
alias_array[16]="alias gcob=\"/scripts/git/checkout.sh\""
alias_array[17]="alias ghub=\"/scripts/git/hub.sh\""
for i in "${alias_array[@]}";
do
if ! grep -q "$i"  $modify_file; then
 echo "$i" >> $modify_file
fi
done
