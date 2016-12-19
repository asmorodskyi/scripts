#!/bin/bash
modify_file=~/.bashrc
alias_array[1]="alias gco=\"git checkout\""
alias_array[2]="alias gpl=\"git pull\""
alias_array[3]="alias gph=\"git push\""
alias_array[4]="alias gst=\"git status\""
alias_array[5]="alias gad=\"git add .\""
alias_array[6]="alias gcim=\"git commit --amend\""
alias_array[7]="alias gphf=\"git push -f\""
alias_array[8]="alias grhh=\"git reset --hard HEAD\""
for i in "${alias_array[@]}";
do
if ! grep -q $i  $modify_file; then
 echo "$i - NOT EXISTS"
 else 
   echo "$i"
fi
done