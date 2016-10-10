@echo off
SET /p channel="Enter channel to join: "
SET /p logging_level="Enter logging level (nil for Info): "
cmd /k "python StrongLegsBot.py #%channel% %logging_level%"
