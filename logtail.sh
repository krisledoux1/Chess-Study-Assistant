#!/bin/bash
mytitle="Log Tailer csa.log"
echo -e '\033]2;'$mytitle'\007'
tail -F csa.log



