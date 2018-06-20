#!/bin/sh -x
# --subject-prefix
git format-patch -n HEAD^
git send-email --to ltp@lists.linux.it $(ls | grep 000*)
rm $(ls | grep 000*)