#!/bin/bash
mytitle="Log Tailer chess_stats.log"
echo -e '\033]2;'$mytitle'\007'
tail -F chess_stats.log



